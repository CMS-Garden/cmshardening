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

import re
import subprocess
import sys

from hardening import core
from hardening.info.lib.PackageManager import PackageManager


class PHPConfig(object):
    """
    collects and provides information about the locally installed PHP environment
    """

    def __init__(self):
        self.__versioninfo = dict()
        self.__versioninfo['PHP version'] = ""
        self.read_php_version()

    @staticmethod
    def get_version():
        return PackageManager().get_package_manager().get_alt_installed_version("php")

    def read_php_version(self):
        regex_version = re.compile(r'^PHP ([^-]+)')
        cmd = ["php", "-v"]
        try:
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
        except OSError:
            return

        if process.returncode != 0:
            core.LogManager().get_logger().fatal(stderr.strip())
            raise subprocess.CalledProcessError(
                process.returncode, cmd, output=stderr)

        if sys.hexversion < 0x03000000:
            match = regex_version.match(stdout.split(b'\n')[0])
        else:
            match = regex_version.match(stdout.decode('utf-8').split(u'\n')[0])
        if match:
            self.__versioninfo['PHP version'] = match.group(1)
