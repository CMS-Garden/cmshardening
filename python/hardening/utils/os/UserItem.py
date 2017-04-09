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

from hardening import utils, constants, storage


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_USERHOME,
                         required=False, docstring="home directory"),
        utils.UtilOption(constants.OPTION_USERSHELL,
                         required=False, docstring="login shell")
    ],
    required_transaction=storage.PasswdTransaction
)
class UserItem(utils.HardeningUtil):
    """
    creates a user. If the user already exists, it will be modified.
    """

    def __run__(self):
        if self.has_option(constants.OPTION_USERHOME):
            self.transaction().set_pw_dir(self.get_option(constants.OPTION_USERHOME))

        if self.has_option(constants.OPTION_USERSHELL):
            self.transaction().set_pw_shell(self.get_option(constants.OPTION_USERSHELL))
