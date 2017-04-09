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

import subprocess
from hardening import core
from hardening.storage import StorageHandler
from hardening.storage.Transaction import Transaction


@StorageHandler("cmd")
class CommandTransaction(Transaction):
    """
    base class for transaction that require one or more commands to run. Derived classes must
    implement `get_commit_command()` and `get_rollback_command()` and don't need to worry about
    how these commands are executed
    """

    COMMIT_KEY = "commit_cmd"
    ROLLBACK_KEY = "rollback_cmd"

    def __init__(self, address, commit_cmd=None, rollback_cmd=None):
        # remove the leading object id
        parts = address.split(':')
        self.__random_id = parts[0]
        self.__commit_cmd = commit_cmd
        self.__rollback_cmd = rollback_cmd

        super(CommandTransaction, self).__init__(id(self))

    def inform_user(self, message=""):
        pass

    def set_commit_command(self, commit_cmd):
        self.__commit_cmd = commit_cmd

    def set_rollback_command(self, rollback_cmd):
        self.__rollback_cmd = rollback_cmd

    @property
    def random_id(self):
        return self.__random_id

    def __begin__(self):
        pass

    def __prepare_commit__(self):
        pass

    def __commit__(self):
        self.__run_command(self.get_commit_command)

    def __rollback__(self):
        self.__run_command(self.get_rollback_command)

    @staticmethod
    def __run_command(cmd_method):
        cmd = cmd_method()
        if cmd is None:
            return

        assert isinstance(cmd, list)

        if core.RuntimeOptions().is_log_enabled():
            core.ChangeLog().append_log_item("###########################################")
            core.ChangeLog().append_log_item(" ".join(cmd))

        if core.RuntimeOptions().pretend_mode():
            return

        core.LogManager().get_logger().info("running command: " + " ".join(cmd))
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        if process.returncode != 0:
            core.LogManager().get_logger().fatal(stderr.strip())
            raise subprocess.CalledProcessError(
                process.returncode, cmd, output=stderr)
        else:
            core.LogManager().get_logger().info("success")

    def get_commit_command(self):
        if self.__commit_cmd is None:
            return None
        return self.__commit_cmd

    def get_rollback_command(self):
        if self.__rollback_cmd is None:
            return None
        return self.__rollback_cmd

    def __eq__(self, other):
        return super(CommandTransaction, self).__eq__(other) and \
            self.random_id == other.random_id

    def __hash__(self):
        return hash(self.random_id)

# pylint: disable=no-member
Transaction.register(CommandTransaction)
