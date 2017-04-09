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

import os
import random
import re
import shutil
import tempfile
from datetime import datetime

from hardening import core, info
from hardening.storage import StorageHandler
from hardening.storage.FileAndDirectoryTransaction import FileAndDirectoryTransaction


@StorageHandler("dir")
class DirectoryTransaction(FileAndDirectoryTransaction):
    """
    This class represents the transaction for directory and directory-like objects and cover some
    general information as well as the backup process for directories

    This transaction is a subclass of the FileAndDirectoryTransaction
    """

    def __init__(self, directoryname):
        super(DirectoryTransaction, self).__init__(directoryname)
        self.__directoryname = directoryname
        self.__dir_temp = None
        self.__changelog = list()
        self.__timestamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
        self.__apply_changes = None

    def tmpname(self):
        return self.__dir_temp

    def __begin__(self):
        if os.path.exists(self.__directoryname):
            self.__dir_temp = self.__generate_tmp_dirname(self.__directoryname)

            self.copy_dir(self.__directoryname, self.__dir_temp)
        else:
            core.LogManager().get_logger().debug(
                _("Directory %(dirname)s does not exist and will therefore not be altered."
                  % {'dirname': self.__directoryname}))
            self.__dir_temp = None
            self.__apply_changes = False

    @staticmethod
    def __generate_tmp_dirname(directoryname):
        count = 0
        dir_temp = directoryname + "_temp_" + \
            str(random.randint(100000, 999999))
        while os.path.isdir(dir_temp) and count < 1000:
            dir_temp = directoryname + "_temp_" + \
                str(random.randint(100000, 999999))
            count += 1
        if count >= 1000:
            raise RuntimeError(
                "could not create temporary directory within 1000 tries.")
        return dir_temp

    def __prepare_commit__(self):
        self.__apply_changes = self.must_apply_changes()

    def __commit__(self):
        if self.__apply_changes:
            self.copy_dir(self.__directoryname, self.backup_path())
            shutil.rmtree(self.__directoryname)
            self.copy_dir(self.__dir_temp, self.__directoryname)

            core.LogManager().get_logger().info(
                _("Writing backup for '%(dirname)s' to '%(backuppath)s'."
                  % {'dirname': self.__directoryname,
                     'backuppath': self.backup_path()}))

        if self.__apply_changes and self.is_marked_as_deleted():
            shutil.rmtree(self.__directoryname)
        if self.__dir_temp is not None:
            shutil.rmtree(self.__dir_temp)

    def must_apply_changes(self):
        apply_changes = False
        if core.RuntimeOptions().pretend_mode():
            apply_changes = False
        else:
            if self.__apply_changes is None:
                apply_changes = True

        if core.RuntimeOptions().interactive_mode():
            apply_changes = self.has_something_to_commit()
        return apply_changes

    def __rollback__(self):
        if self.__dir_temp is not None:
            if os.path.exists(self.__dir_temp):
                shutil.rmtree(self.__dir_temp)

    @staticmethod
    def copy_dir(directoryname, new_name):
        if os.path.isdir(new_name):
            raise OSError(
                "Directory already exists, could not move directory.")
        shutil.copytree(directoryname, new_name)
        DirectoryTransaction.transfer_owner(directoryname, new_name)
        for root, dirs, files in os.walk(directoryname):
            new_root = root.replace(directoryname, new_name)
            for current_dir in dirs:
                DirectoryTransaction.transfer_owner(os.path.join(root, current_dir),
                                                    os.path.join(new_root, current_dir))
            for current_file in files:
                DirectoryTransaction.transfer_owner(os.path.join(root, current_file),
                                                    os.path.join(new_root, current_file))

    @staticmethod
    def transfer_owner(src, dst):
        stat = os.stat(src)
        os.chown(dst, stat.st_uid, stat.st_gid)

    def delete(self):
        if self.__dir_temp is not None:
            if core.RuntimeOptions().interactive_mode():
                if not self.prompt_user(_("Do you want to delete '%(dirname)s'?")
                                        % {'dirname': self.__directoryname}):
                    return
            self.append_to_changelog(
                "###########################################")
            self.append_to_changelog(
                "sudo rm -rf %(dirname)s" % {'dirname': self.__directoryname})
            self.__mark_directory_as_deleted()

    def append_to_changelog(self, *lines):
        self.__changelog.extend(lines)

    def __get_change_logs(self):
        return self.__changelog

    def backup_name(self):
        original_name = os.path.split(self.__directoryname)[-1]
        original_path = os.path.join(
            *(os.path.split(self.__directoryname)[:-1]))
        return os.path.join(
            original_path, ('.' + original_name + "_backup_" + self.timestamp()))

    def backup_path(self):
        return os.path.join(re.sub('/$', '', self.backupdir()),
                            re.sub('^/|/$', '', self.backup_name()))

    def timestamp(self):
        return self.__timestamp

    @staticmethod
    def backupdir():
        dirname = info.Configuration().get_property(
            "Backup", "BaseDir", default=tempfile.gettempdir())
        mode = info.Configuration().get_property(
            "Backup", "BaseDirMode", default=0o600)
        if not os.path.exists(dirname):
            os.makedirs(dirname, mode)
        return dirname

    def __mark_directory_as_deleted(self):
        if self.has_modifications_to_save():
            raise core.HardeningFailure(
                _("unable to delete '%(dirname)s' because it has been modified")
                % {'dirname': self.__directoryname})
        self.mark_as_deleted()


# pylint: disable=no-member
FileAndDirectoryTransaction.register(DirectoryTransaction)
