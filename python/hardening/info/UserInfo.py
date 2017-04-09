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

from hardening.info import InfoHandler


@InfoHandler("user")
# pylint: disable=too-few-public-methods
class UserInfo(object):
    """
    provides information about users on the local system
    """

    @staticmethod
    def get_logname(*_):
        """returns the name with which the user has logged in to the current system.

        This is normally your current username. But: If you used `sudo` to become another user, then
        this interpolates to your username you had *before* you invoked `sudo`
        """
        return os.getlogin()
