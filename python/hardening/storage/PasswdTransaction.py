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

import pwd
import os
import subprocess
import psutil
from hardening import core
from hardening.storage import StorageHandler
from hardening.info import lib
from hardening.storage.CommandTransaction import CommandTransaction


@StorageHandler("passwd")
class PasswdTransaction(CommandTransaction):
    """
    Transaction for passwd changes, e.g. creating or modifying users
    this class is a sublass of CommandTransaction
    """

    def __init__(self, username, **_):

        super(PasswdTransaction, self).__init__(str(id(self)))

        self.__username = username
        assert self.__username is not None
        self.__pw_dir = None
        self.__pw_shell = None
        self.__create_user = None
        self.__original_user = None

    def __begin__(self):

        for proc in psutil.process_iter():
            if self.__username == proc.username():
                raise core.HardeningFailure(
                    _("User %(username)s has running processes, you cannot modify that user.")
                    % {'username': self.__username})

        if not lib.Passwd().has_passwd_entry(self.__username):
            process = subprocess.Popen(["/usr/sbin/useradd", self.__username],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            # pylint: disable=unused-variable
            stdin, stderr = process.communicate()
            if process.returncode != 0:
                core.LogManager().get_logger().fatal(stderr.strip())
                raise subprocess.CalledProcessError(
                    process.returncode, ["/usr/sbin/useradd", self.__username], output=stderr)
            else:
                self.__create_user = True
        else:
            self.__create_user = False

    def set_pw_dir(self, directory):
        if self.__pw_dir is not None and self.__pw_dir != directory:
            raise RuntimeError("conflicting values for user home directory: '%s' and '%s'"
                               % (directory, self.__pw_dir))

        if self.__pw_dir is None:
            self.__pw_dir = directory

    def set_pw_shell(self, shell):
        if self.__pw_shell is not None and self.__pw_shell != shell:
            raise RuntimeError("conflicting values for user shell: '%s' and '%s'"
                               % (shell, self.__pw_shell))

        if self.__pw_shell is None:
            self.__pw_shell = shell

    def get_commit_command(self):
        option_values = list()
        has_changes = False
        current_homedir = None
        current_shell = None

        try:
            self.__original_user = pwd.getpwnam(self.__username)
            current_homedir = self.__original_user[5]
            current_shell = self.__original_user[6]
            option_values.extend(["/usr/sbin/usermod", self.__username])
        except KeyError:
            option_values.extend(["/usr/sbin/useradd", self.__username])
            self.__create_user = True
            has_changes = True

        has_changes, opts = self.__get_homedir_arguments(current_homedir, has_changes)
        option_values.extend(opts)

        if self.__pw_shell is not None:
            if current_shell is not None and self.__pw_shell == current_shell:
                pass
            else:
                option_values.extend(["-s", self.__pw_shell])
                has_changes = True

        if has_changes:
            return option_values
        else:
            return None

    def __get_homedir_arguments(self, current_homedir, has_changes):
        opts = []
        if self.__pw_dir is not None:
            if current_homedir is not None and self.__pw_dir == current_homedir:
                pass
            else:

                # prevent usermod from raising E_HOMEDIR (12)
                if not os.path.exists(self.__pw_dir):
                    if current_homedir is not None and not os.path.isdir(
                            current_homedir):
                        core.LogManager().get_logger().warning(
                            _("directory %(dirname)s is not a directory and will not be moved")
                            % {'dirname': self.__pw_dir})
                    else:
                        opts.append("-m")
                elif not os.path.isdir(self.__pw_dir):
                    raise core.HardeningFailure(_("directory %(dirname)s is not a directory"
                                                  % {'dirname': self.__pw_dir}))
                else:
                    opts.extend(["-d", self.__pw_dir])
                has_changes = True
        return has_changes, opts

    def get_rollback_command(self):
        option_values = list()

        if self.__create_user:
            option_values.extend(["/usr/sbin/userdel", self.__username])
        elif self.__original_user is not None:
            option_values.extend(["/usr/sbin/usermod", self.__username])
            if self.__pw_dir is not None:
                option_values.extend(["-d", self.__original_user[5]])

            if self.__pw_shell is not None:
                option_values.extend(["-s", self.__original_user[6]])

            if self.__pw_dir is None and self.__pw_shell is None:
                return None
        else:
            # nothing to roll back
            return None
        return option_values
