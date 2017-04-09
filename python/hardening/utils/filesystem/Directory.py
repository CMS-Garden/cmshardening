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

from hardening import utils, constants


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_PATH, required=True,
                         docstring="complete path of the new directory")
    ])
class Directory(utils.HardeningUtil):
    """
    creates a directory
    """

    def __run__(self):
        path = self.get_option(constants.OPTION_PATH)

        # create the directory
        if not os.path.exists(path):
            os.mkdir(path, 0o700)
