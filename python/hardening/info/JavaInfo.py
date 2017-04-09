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

from hardening.info import InfoHandler
from hardening.info.lib import PackageManager


@InfoHandler("java")
# pylint: disable=too-few-public-methods
class JavaInfo(object):
    """
    provides information about the currently installed java runtime environment
    """

    @staticmethod
    def get_current_version(*_):
        return PackageManager().get_package_manager().get_alt_upgradeable_version("java")
