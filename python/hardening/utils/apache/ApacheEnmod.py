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


@utils.ModuleSettings(options=[
    utils.UtilOption(constants.OPTION_MODNAME,
                     required=True,
                     docstring="name of the apache module to be enabled")
])
class ApacheEnmod(hardening.utils.CommandUtil.CommandUtil):
    """
    this module runs a2enmod to enable an apache module
    """

    def get_commit_command(self):
        assert self.get_option(constants.OPTION_MODNAME) != '*'
        return ["a2enmod", self.get_option(constants.OPTION_MODNAME)]

    def get_rollback_command(self):
        return ["a2dismod", "-q", "-f",
                self.get_option(constants.OPTION_MODNAME)]
