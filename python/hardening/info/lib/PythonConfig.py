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

import sys
from hardening.info.lib.PackageManager import PackageManager


class PythonConfig(object):
    """
    determines and provides information about the locally installed Python environment
    """

    def __init__(self):
        self.__versioninfo = dict()
        self.__versioninfo['python version'] = ""
        self.read_python_version()

    @staticmethod
    def get_version():
        version_info = PackageManager().get_package_manager(
        ).get_package_upgrade_info("python")
        if version_info is None:
            return None
        return version_info[1]

    def read_python_version(self):
        self.__versioninfo['python version'] = "%s.%s.%s" % (
            sys.version_info[0], sys.version_info[1], sys.version_info[2])
