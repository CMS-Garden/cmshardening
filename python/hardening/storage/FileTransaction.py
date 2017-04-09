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

import errno
import os
import shutil
import tempfile
import subprocess

from hardening import core
from hardening.storage.TransactionInfo import TransactionInfo
from hardening.storage.FileAndDirectoryTransaction import FileAndDirectoryTransaction


# pylint: disable=too-many-instance-attributes
class FileTransaction(FileAndDirectoryTransaction):
    """
    This class represent the transaction for file and file like object and cover some general
    information as well as the backup process for files
    this transaction is a subclass of the FileAndDirectoryTransaction
    """

    def __init__(self, filename):
        super(FileTransaction, self).__init__(filename)
        self.__filename = filename
        self.__fd = None
        self.__fdtemp = None
        self.__tmpname = None
        self.__lines = None
        self.__apply_changes = False

        # this will be overwritten in __begin__
        self.__original_file_exists = False

        self.__changelog = list()
        self.__actions = list()

    def tmpname(self):
        return self.__tmpname

    def __begin__(self):
        """
        We create the temporary file first and close it immediately.
        Then we reopen the file. The difference is that NamedTemporaryFile()
        does not return a file object, but a wrapper to a file object. This
        has caused some strange effects which disappeared after we've closed
        the tempfile and reopened as file object
        """
        try:
            self.__fdtemp = tempfile.NamedTemporaryFile(
                prefix=os.path.basename(self.__filename) + "_",
                dir=os.path.dirname(self.__filename),
                delete=False)
        except OSError:
            self.__fdtemp = tempfile.NamedTemporaryFile(
                prefix=os.path.basename(self.__filename) + "_",
                delete=False)

        self.__tmpname = self.__fdtemp.name
        self.__fdtemp.close()

        self.__fdtemp = open(self.__tmpname, "w+")

        try:
            self.__fd = open(self.__filename, "r+")
            self.__original_file_exists = True

            FileTransaction.transfer_owner(self.__filename, self.__fdtemp.name)
            FileTransaction.transfer_perm(self.__filename, self.__fdtemp.name)

        except IOError as error:
            if error.errno == errno.ENOENT:  # no such file or directory
                self.__fd = None
                self.__original_file_exists = False
            else:
                raise error

    @staticmethod
    def transfer_owner(src, dst):
        stat = os.stat(src)
        os.chown(dst, stat.st_uid, stat.st_gid)

    @staticmethod
    def transfer_perm(src, dst):
        stat = os.stat(src)
        os.chmod(dst, stat.st_mode)

    def __commit__(self):
        self.write_to_tempfile()

        if core.RuntimeOptions().is_log_enabled():
            self.log_changes()

        self.__write_changes_and_backup()

    def __prepare_commit__(self):
        self.__apply_changes |= self.must_apply_changes() or self.is_marked_as_deleted()

    def __rollback__(self):
        tmpname = self.__fdtemp.name
        self.__fdtemp.close()
        if os.path.exists(tmpname):
            os.unlink(tmpname)

        if self.__fd is not None:
            self.__fd.close()

    def delete(self):
        assert self.is_transaction_running()
        if os.path.exists(self.__filename):
            if core.RuntimeOptions().interactive_mode():
                if not self.prompt_user(_("Do you want to delete '%(filename)s'?")
                                        % {'filename': self.__filename}):
                    return
            self.append_to_changelog(
                "###########################################")
            self.append_to_changelog("sudo rm -f %(filename)s"
                                     % {'filename': self.__filename})
            self.__mark_file_as_deleted()
        else:
            core.LogManager().get_logger().debug(
                _("The file %(filename)s does not exists and will therefore not be deleted")
                % {'filename': self.__filename})

    # pylint: disable=no-self-use
    def must_apply_changes(self):
        return True

    def append_to_changelog(self, *lines):
        self.__changelog.extend(lines)

    def log_changes(self):
        for log_entry in self.__get_change_logs():
            core.ChangeLog().append_log_item(log_entry)

    def mark_as_modified(self):
        if self.is_marked_as_deleted():
            raise core.HardeningFailure(
                _("unable to modify '%(filename)s' because it has been deleted")
                % {'filename': self.__filename})
        super(FileTransaction, self).mark_as_modified()

    def read(self, *args):
        if self.__fd is None:
            return None
        self.__fd.seek(0)
        return self.__fd.read(*args)

    def readlines(self, *args):
        if self.__fd is None:
            return []
        self.__fd.seek(0)
        return self.__fd.readlines(*args)

    def new_file_content(self):
        return self.__fd.read()

    def __get_change_logs(self):
        return self.__changelog

    def write_to_tempfile(self):
        core.LogManager().get_logger().info(_("storing to: %(tempname)s")
                                            % {'tempname': self.__fdtemp.name})
        self.__fdtemp.write(self.new_file_content())

    def __write_changes_and_backup(self):

        def force_link(filename, linkname):
            command = ["/bin/ln", "-f", filename, linkname]
            core.LogManager().get_logger().info(_("invoking: %(command)s")
                                                % {'command': command})
            process = subprocess.Popen(command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            # pylint: disable=unused-variable
            stdin, stderr = process.communicate()

            if process.returncode != 0:
                core.LogManager().get_logger().fatal(stderr.strip())
                raise subprocess.CalledProcessError(
                    process.returncode, command, output=stderr)
            else:
                core.LogManager().get_logger().info("success")

        # execute misc actions, such as chown and chmod
        for action in self.__actions:
            action()

        if self.__apply_changes and self.has_something_to_commit():
            if self.__original_file_exists:
                # create temporary backup file, which will be moved later to
                # the backup folder.
                force_link(self.__filename, self.__backup_path())

            # replace the original file with the newly created file
            if not self.is_marked_as_deleted():
                self.create_directory(os.path.dirname(self.__filename))
                force_link(self.__fdtemp.name, self.__filename)

        # close original and temporary file
        self.__fdtemp.close()
        if self.__fd is not None:
            self.__fd.close()

        # delete original file
        if self.is_marked_as_deleted() and self.__original_file_exists and self.__apply_changes:
            core.LogManager().get_logger().debug(_("deleting file '%(filename)s'")
                                                 % {'filename': self.__filename})
            os.unlink(self.__filename)

        # unlink the temporary file. if __delete_file is False,
        # there should be an additional hardlink to the file.
        # if not, the file will be deleted
        os.unlink(self.__tmpname)
        if self.__original_file_exists and self.__apply_changes and self.has_something_to_commit():
            shutil.move(self.__backup_path(), self.backup_path())

        if self.__apply_changes and self.has_something_to_commit():
            core.LogManager().get_logger().info(
                _("Writing backup for '%(filename)s' to '%(backuppath)s'."
                  % {'filename': self.__filename,
                     'backuppath': self.backup_path()}))
        else:
            core.LogManager().get_logger().debug(
                _("Omitting backup for '%(filename)s' because nothing had to be changed"
                  % {'filename': self.__filename}))

    @staticmethod
    def create_directory(directory):
        path = ""
        for path_component in os.path.split(directory):
            path = os.path.join(path, path_component)
            if not os.path.exists(path):
                os.mkdir(path, 0o755)

    def backup_path(self):
        backupdir = TransactionInfo().get_backupdir(os.path.dirname(self.__filename))
        return os.path.join(backupdir, os.path.basename(self.__filename))

    def __backup_name(self):
        original_name = os.path.basename(self.__filename)
        return '.' + original_name + "_backup_" + TransactionInfo().get_timestamp()

    def __backup_path(self):
        filename_parts = list(os.path.split(self.__filename))
        filename_parts[-1] = self.__backup_name()
        return os.path.join(*filename_parts)

    def __mark_file_as_deleted(self):
        if self.has_modifications_to_save():
            raise core.HardeningFailure(
                _("unable to delete '%(filename)s' because it has been modified")
                % {'filename': self.__filename})
        self.mark_as_deleted()


# pylint: disable=no-member
FileAndDirectoryTransaction.register(FileTransaction)
