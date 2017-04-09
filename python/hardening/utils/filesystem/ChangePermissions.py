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
from hardening import storage, utils, constants


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_MODE,
                         required=True,
                         docstring="mode to be used as new access permissions"),
        utils.UtilOption(constants.OPTION_RECURSIVE,
                         required=False,
                         docstring="additional parameter for ChangeOwner"),
        utils.UtilOption(constants.OPTION_APPLY_TO_FILES,
                         required=False,
                         docstring=""),
        utils.UtilOption(constants.OPTION_APPLY_TO_DIRECTORIES,
                         required=False,
                         docstring="")
    ],
    required_transaction=storage.FileAndDirectoryTransaction)
class ChangePermissions(utils.HardeningUtil):
    """
    this class can be used to change the access permissions of a file. The mode
    must be a valid octal number between `000` and `777`.
    """

    def __init__(self, *args, **kwargs):
        utils.HardeningUtil.__init__(self, *args, **kwargs)
        self.__mode = None

    def __setup__(self):
        self.__mode = self.get_option(constants.OPTION_MODE)

    def __run__(self):
        if os.path.isfile(self.transaction().url()):
            apply_to_files = True
        else:
            apply_to_files = self.get_option(constants.OPTION_APPLY_TO_FILES)
        self.transaction().chmod(self.__mode,
                                 self.get_option(constants.OPTION_RECURSIVE),
                                 apply_to_files,
                                 self.get_option(constants.OPTION_APPLY_TO_DIRECTORIES))
