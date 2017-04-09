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
import os
import sys
import subprocess
from hardening.info.lib.PackageManager import PackageManager

from hardening import core


class JavaConfig(object):
    """obtains information about the locally installed java version

    """

    def __init__(self):
        self.__versioninfo = dict()
        self.__versioninfo['Java version'] = ""
        self.read_java_version()

    @staticmethod
    def get_version():
        """ obtains the version of the installed Java VM

        The command `java -version` is being used to obtain the version

        @return version as string
        """
        return PackageManager().get_package_manager().get_alt_installed_version("java")

    def read_java_version(self):
        regex_version = re.compile(r'^.*"(.*?)"')
        cmd = ["java", "-version"]
        try:
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            _, stderr = process.communicate()
        except OSError:
            return

        if process.returncode != 0:
            core.LogManager().get_logger().fatal(stderr.strip())
            raise subprocess.CalledProcessError(
                process.returncode, cmd, output=stderr)

        # For some reason the subprocessPopen output is written in stderr and not stdout
        # like expected
        if sys.hexversion < 0x03000000:
            match = regex_version.match(stderr.split(os.linesep)[0])
        else:
            match = regex_version.match(
                stderr.decode('utf-8').split(os.linesep)[0])

        if match:
            self.__versioninfo['Java version'] = match.group(1)
