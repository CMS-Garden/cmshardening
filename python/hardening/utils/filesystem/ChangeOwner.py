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
from hardening import utils, core, storage, constants
from hardening.info import lib


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_USER, required=True,
                         docstring="name of the new owner"),
        utils.UtilOption(constants.OPTION_GROUP, required=False,
                         docstring="name of the owning group"),
        utils.UtilOption(constants.OPTION_RECURSIVE, required=False,
                         docstring="additional parameter for ChangeOwner"),
        utils.UtilOption(constants.OPTION_APPLY_TO_FILES,
                         required=False, docstring=""),
        utils.UtilOption(constants.OPTION_APPLY_TO_DIRECTORIES,
                         required=False, docstring="")
    ],
    required_transaction=storage.FileAndDirectoryTransaction)
class ChangeOwner(utils.HardeningUtil):
    """
    this class can be used to change the owner (and, if necessary, the owning group) of a file
    """

    def __init__(self, *args, **kwargs):
        utils.HardeningUtil.__init__(self, *args, **kwargs)
        self.__uid = -1
        self.__gid = -1

    def __setup__(self):
        user = self.get_option(constants.OPTION_USER)
        group = self.get_option(constants.OPTION_GROUP)

        if user is not None:
            if lib.Passwd().has_passwd_entry(user):
                self.__uid = lib.Passwd().get_uid(user)
            else:
                raise core.HardeningFailure(_("invalid user name: '%(user)s'")
                                            % {'user': user})
        if group is not None:
            if lib.Group().has_group_entry(group):
                self.__gid = lib.Group().get_gid(group)
            else:
                raise core.HardeningFailure(_("invalid group name: '%(group)s'")
                                            % {'group': group})

    def __run__(self):
        if os.path.isfile(self.transaction().url()):
            apply_to_files = True
        else:
            apply_to_files = self.get_option(constants.OPTION_APPLY_TO_FILES)
        self.transaction().chown(self.__uid, self.__gid,
                                 self.get_option(constants.OPTION_RECURSIVE),
                                 apply_to_files,
                                 self.get_option(constants.OPTION_APPLY_TO_DIRECTORIES))
