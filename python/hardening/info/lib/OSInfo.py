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

import platform
try:
    import distro
except ImportError:
    # pylint: disable=reimported
    import platform as distro
from hardening import core


@core.singleton
class OSInfo(object):
    """
    provides information about the local operating system
    """

    def __init__(self):
        self.__package_manager = None
        _system = platform.system()
        if _system == "Linux":
            _system = distro.linux_distribution()[0]

        self.__system = "%s:%s:%s" % \
            (_system, platform.release(), platform.version())

    def distribution_name(self):
        return self.__system

    @staticmethod
    def os_name():
        return platform.system()

    @staticmethod
    def os_version():
        return platform.version()

    @staticmethod
    def os_uname():
        return platform.uname()
