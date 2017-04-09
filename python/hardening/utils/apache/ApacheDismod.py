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
import hardening.utils.CommandUtil
from hardening import utils, constants
from hardening.info import lib


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_MODNAME, required=True,
                         docstring="name of the apache module to be disabled")
    ])
class ApacheDismod(hardening.utils.CommandUtil.CommandUtil):
    """
    this module runs a2dismod to disable an apache module
    """

    def __init__(self, **kwargs):
        super(ApacheDismod, self).__init__(**kwargs)
        self.__enabled_modules = None

    def get_commit_command(self):
        command = ["a2dismod", "-q", "-f"]
        if self.get_option(constants.OPTION_MODNAME) == '*':
            self.__enabled_modules = lib.ApacheConfig().get_enabled_modules()
        else:
            self.__enabled_modules = [
                self.get_option(constants.OPTION_MODNAME)]

        command.extend(self.__enabled_modules)
        return command

    def get_rollback_command(self):
        command = ["a2enmod"]
        command.extend(self.__enabled_modules)
        return command
