# This file is part of BSICMS2.
#
# BSICMS2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import grp
import os
import pwd
import stat
import re

from abc import ABCMeta, abstractmethod

# noinspection PyBroadException
try:
    # noinspection PyShadowingBuiltins,PyUnresolvedReferences
    # pylint: disable=redefined-builtin
    import itertools.filter as filter
except ImportError:
    pass

from six import with_metaclass
from hardening import core
from hardening.storage.Transaction import Transaction


class FileAndDirectoryTransaction(with_metaclass(ABCMeta, Transaction)):
    """
    this class is the parent for the FileTransaction and the DirectoryTransaction
    it covers functions which can be applied to both files and directories like chmod and chwon
    and has abstract methods for functions that need to be individualy addressed like delete
    """

    def __init__(self, *args, **kwargs):
        super(FileAndDirectoryTransaction, self).__init__(*args, **kwargs)
        self.__is_marked_as_deleted = False

    def chown(self, uid, gid, recursive=False,
              apply_to_file=False, apply_to_directory=True):
        assert isinstance(uid, int)
        assert isinstance(gid, int)

        if self.tmpname() is None:
            return

        if not os.path.isdir(self.tmpname()):
            recursive = False

        to_modify_list = list()

        # check if something has to be changed
        def check_action(tupel):
            return self.check_chown(tupel[1], uid, gid)

        # append temp dir and original dir as tupel to to_modify__list
        def list_action(temp_dir, original_dir):
            return to_modify_list.append((temp_dir, original_dir))

        # enumerate all child filesystem entry
        self.__visit(self.tmpname(), self.url(), list_action, recursive,
                     apply_to_file, apply_to_directory)
        # select entries with settings that must be changed (e.g. invalid
        # owner)
        filtered_list = list(filter(check_action, to_modify_list))
        if len(filtered_list) > 0:
            if self.__prompt_user_chown(uid, gid, recursive):
                self.mark_as_modified()
                for entry in filtered_list:
                    self.do_chown(entry[0], entry[1], uid, gid)
        else:
            self.inform_user(
                message=_("Ownership already set as expected."))

    @staticmethod
    def check_chown(original_path, uid, gid):
        stat_result = os.stat(original_path)
        if (uid == -1 or uid == stat_result.st_uid) and (gid == -
                                                         1 or gid == stat_result.st_gid):
            return False
        return True

    def do_chown(self, temp_path, original_path, uid, gid):
        os.chown(temp_path, uid, gid)
        if core.RuntimeOptions().is_log_enabled():
            if uid != -1 and gid != -1:
                self.add_change_command("chown %d:%d '%s'" %
                                        (uid, gid, original_path))
            elif uid == -1 and gid != -1:
                self.add_change_command("chgrp %d '%s'" % (gid, original_path))
            elif uid != -1 and gid == -1:
                self.add_change_command("chown %d '%s'" % (uid, original_path))
            else:
                raise RuntimeError(_("chown: no changes"))

    def chmod(self, mode, recursive=False, apply_to_file=False,
              apply_to_directory=True):
        if self.tmpname() is None:
            return

        if isinstance(mode, str):
            # parse mode string
            mode_action = self.parse_mode(mode)
        else:
            def mode_action(_):
                return mode

        if not os.path.isdir(self.tmpname()):
            recursive = False

        to_modify_list = list()

        # check if something has to be changed
        def check_action(tupel):
            return self.check_chmod(tupel[0], mode_action)

        # append temp dir and original dir as tupel to to_modify__list
        def list_action(temp_dir, original_dir):
            return to_modify_list.append((temp_dir, original_dir))

        # enumerate all child filesystem entry
        self.__visit(self.tmpname(), self.url(), list_action, recursive,
                     apply_to_file, apply_to_directory)

        # select entries with settings that must be changed (e.g. invalid
        # owner)
        filtered_list = list(filter(check_action, to_modify_list))

        if len(filtered_list) > 0:
            if self.__prompt_user_chmod(mode, recursive):
                self.mark_as_modified()
                for entry in filtered_list:
                    self.do_chmod(entry[0], entry[1], mode_action)
        else:
            self.inform_user(
                message=_("Permissions already set as expected."))

    @staticmethod
    def check_chmod(temp_path, mode_action):
        current_mode = stat.S_IMODE(os.stat(temp_path).st_mode)
        mode = mode_action(current_mode)
        if current_mode == mode:
            return False
        return True

    def do_chmod(self, temp_path, original_path, mode_action):
        current_mode = stat.S_IMODE(os.stat(temp_path).st_mode)
        os.chmod(temp_path, mode_action(current_mode))
        if core.RuntimeOptions().is_log_enabled():
            self.add_change_command("chmod %s '%s'" % (oct(mode_action(current_mode)),
                                                       original_path))

    @staticmethod
    def parse_mode(mode):
        try:
            # this must be done in two steps, to raise ValueError befor the
            # lambda is being called
            numeric_mode = int(mode, 8)
            return lambda _: numeric_mode
        except ValueError:
            pass

        regex = re.compile(r"(a|u?g?o?)([-+=])(r?w?x?s?t?)")
        match = regex.match(mode)
        if not match:
            raise SyntaxError(_("invalid mode specified: '%(mode)s'")
                              % {'mode': mode})

        tmpmask = 0
        mask = 0
        if 'r' in match.group(3):
            tmpmask |= 0o4
        if 'w' in match.group(3):
            tmpmask |= 0o2
        if 'x' in match.group(3):
            tmpmask |= 0o1

        if match.group(1) == "a" or 'u' in match.group(1):
            mask |= tmpmask << 6
        if match.group(1) == "a" or 'g' in match.group(1):
            mask |= tmpmask << 3
        if match.group(1) == "a" or 'o' in match.group(1):
            mask |= tmpmask

        if match.group(2) == '-':
            return lambda current_mode: current_mode & ~mask
        elif match.group(2) == '+':
            return lambda current_mode: current_mode | mask
        else:  # =
            return lambda _: mask

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def tmpname(self):
        pass

    def __prompt_user_chown(self, uid, gid, recursive):
        if core.RuntimeOptions().interactive_mode():
            additional_info = ""
            if recursive:
                additional_info = _("(recursive)")
            if uid != -1:
                username = pwd.getpwuid(uid)[0]
                if not self.prompt_user(
                        _("Do you want to give user %(user)s the ownership of '%(file)s' "
                          "and its contents? %(info)s")
                        % {'user': username,
                           'file': self.url(),
                           'info': additional_info}):
                    return False
            if gid != -1:
                group = grp.getgrgid(gid)[0]
                if not self.prompt_user(
                        _("Do you want to give group %(group)s the ownership of '%(file)s'"
                          "and its contents? %(info)s")
                        % {'group': group,
                           'file': self.url(),
                           'info': additional_info}):
                    return False
        return True

    def __prompt_user_chmod(self, mode, recursive):
        if core.RuntimeOptions().interactive_mode():
            additional_info = ""
            if recursive:
                additional_info = "(recursively)"
            if not self.prompt_user(
                    _("Do you want to set permissions of '%(file)s' to '%(mode)s'? "
                      "%(info)s")
                    % {'file': self.url(),
                       'mode': "".join(self.__get_mode(mode)),
                       'info': additional_info}):
                return False
        return True

    @staticmethod
    def __visit(tmp_basedir, original_basedir, action, recursive,
                apply_to_file, apply_to_directory):
        if os.path.isdir(tmp_basedir):
            for root, dirs, files in os.walk(tmp_basedir):
                if root != tmp_basedir and not recursive:
                    continue

                log_root = root.replace(tmp_basedir, original_basedir)

                if apply_to_directory:
                    for current_dir in dirs:
                        # don't operate on the directory directly; use a
                        # transaction instead
                        action(os.path.join(root, current_dir),
                               os.path.join(log_root, current_dir))

                if apply_to_file:
                    for current_file in files:
                        # don't operate on the file directly, use a
                        # transaction instead
                        action(os.path.join(root, current_file),
                               os.path.join(log_root, current_file))

        if os.path.isfile(tmp_basedir) and apply_to_file or \
                os.path.isdir(tmp_basedir) and apply_to_directory:
            action(tmp_basedir, original_basedir)

    @staticmethod
    def __get_mode(mode):
        if not isinstance(mode, int):
            try:
                mode = int(mode, base=8)
            except ValueError:
                return mode
        display_mode = list('-' * 9)
        if mode & 0o400:
            display_mode[0] = 'r'
        if mode & 0o200:
            display_mode[1] = 'w'
        if mode & 0o100:
            display_mode[2] = 'x'
        if mode & 0o040:
            display_mode[3] = 'r'
        if mode & 0o020:
            display_mode[4] = 'w'
        if mode & 0o010:
            display_mode[5] = 'x'
        if mode & 0o004:
            display_mode[6] = 'r'
        if mode & 0o002:
            display_mode[7] = 'w'
        if mode & 0o001:
            display_mode[8] = 'x'
        return "".join(display_mode)

    def has_something_to_commit(self):
        return self.has_modifications_to_save() or self.is_marked_as_deleted()

    def mark_as_deleted(self):
        self.__is_marked_as_deleted = True

    def is_marked_as_deleted(self):
        return self.__is_marked_as_deleted
