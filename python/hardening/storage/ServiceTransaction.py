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
from hardening.storage.CommandTransaction import CommandTransaction

SERVICESTATE_ENABLED = "enabled"
SERVICESTATE_DISABLED = "disabled"

VALID_ACTIONS = {
    SERVICESTATE_ENABLED: "enable",
    SERVICESTATE_DISABLED: "disable"
}
SERVICEACTION_ENABLE = "enable"
SERVICEACTION_DISABLE = "disable"
SERVICEACTION_START = "start"
SERVICEACTION_STOP = "stop"

ROLLBACK_ACTIONS = {
    SERVICEACTION_ENABLE: SERVICEACTION_DISABLE,
    SERVICEACTION_DISABLE: SERVICEACTION_DISABLE,
    SERVICEACTION_START: SERVICEACTION_STOP,
    SERVICEACTION_STOP: SERVICEACTION_START
}


@StorageHandler("service")
class ServiceTransaction(CommandTransaction):
    """
    Transaction class for os service allowing starting, stopping, enabling and disabling of services
    is a subclass of the command transaction
    """

    def __init__(self, svcname, **_):

        super(ServiceTransaction, self).__init__(svcname)

        self.__svcname = svcname
        self.__new_state = None
        self.__commit_action = None
        self.__rollback_action = None

    def enable_service(self):
        if self.__commit_action is not None and self.__commit_action != SERVICESTATE_ENABLED:
            raise RuntimeError(_("conflicting service states"))
        self.__commit_action = SERVICEACTION_ENABLE
        self.__new_state = SERVICESTATE_ENABLED

    def disable_service(self):
        if self.__commit_action is not None and self.__commit_action != SERVICESTATE_DISABLED:
            raise RuntimeError(_("conflicting service states"))
        self.__commit_action = SERVICEACTION_DISABLE
        self.__new_state = SERVICESTATE_DISABLED

    def stop_service(self):
        assert self.__commit_action is None
        self.__commit_action = SERVICEACTION_STOP

    def start_service(self):
        assert self.__commit_action is None
        self.__commit_action = SERVICEACTION_STOP

    def get_commit_command(self):
        if self.__commit_action is None:
            return None

        if self.__new_state is not None:
            status = self.get_status()

            if status != self.__new_state:
                self.__rollback_action = VALID_ACTIONS[status]
                return ["/bin/systemctl", self.__commit_action, self.__svcname]
        else:
            self.__rollback_action = ROLLBACK_ACTIONS[self.__commit_action]
            return ["/bin/systemctl", self.__commit_action, self.__svcname]

    def get_rollback_command(self):
        if self.__new_state is None or self.__rollback_action is None:
            return None

        return ["/bin/systemctl", self.__rollback_action, self.__svcname]

    def get_status(self):
        cmd = ["/bin/systemctl", "is-enabled", self.__svcname]
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if process.returncode != 0:
            core.LogManager().get_logger().fatal(stderr.strip())
            return SERVICESTATE_DISABLED
        #            raise subprocess.CalledProcessError(
        #                process.returncode, cmd, output=stderr)

        return stdout.strip()
