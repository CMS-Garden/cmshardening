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
import subprocess
from abc import ABCMeta, abstractmethod
from six import with_metaclass
from hardening import core


@core.singleton
# pylint: disable=too-few-public-methods
class PackageManager(object):
    """
    PackageManager returns an AbstractPackageManager-Implementation which is compatible to the
    current operating system
    """

    def __init__(self):
        super(PackageManager, self).__init__()
        self.__package_manager = None

    def get_package_manager(self):
        if self.__package_manager is None:
            self.__package_manager = DebianPackageManager()
        return self.__package_manager


class AbstractPackageManager(with_metaclass(ABCMeta)):
    """
    default interface for all Package Managers (such as dpkg, yum, emerge, ...)
    """

    def __init__(self):
        pass

    @abstractmethod
    def is_package_installed(self, packagename):
        pass

    @abstractmethod
    def get_package_files(self, packagename, filename_regex=None):
        return None


class DebianPackageManager(AbstractPackageManager):
    """
    Implementation of AbstractPackageManager for Debian (dpkg).
    Requires dpkg, dpkg-query, aptitude, update-alternatives
    """

    def __init__(self):
        super(DebianPackageManager, self).__init__()

    def is_package_installed(self, packagename):
        cmd = ["/usr/bin/dpkg-query", "-s", packagename]
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.communicate()
        return process.returncode == 0

    @staticmethod
    def get_package_version(packagename):
        cmd = ["/usr/bin/dpkg-query", "--show", r"--showformat=${Package} ${Version}\n",
               packagename]
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, _ = process.communicate()

        if process.returncode != 0:
            return None

        lines = stdout.decode('utf8').split(os.linesep)
        if len(lines) < 1:
            return None

        (package, version) = lines[0].split(b" ")
        return package, version

    @staticmethod
    def get_package_upgrade_info(package_pattern):
        cmd = ["/usr/bin/aptitude",
               "-F",
               "%p*%v*%V",
               "--disable-columns",
               "search",
               "^" + package_pattern + "$"]
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, _ = process.communicate()

        if process.returncode != 0:
            return None

        lines = stdout.decode('utf8').split(os.linesep)
        if len(lines) < 1:
            return None
        (package, installed_version, current_version) = str(
            lines[0]).split("*")
        if installed_version == "<none>":
            installed_version = None
        return package, installed_version, current_version

    def get_package_files(self, packagename, filename_regex=None):
        try:
            output = subprocess.check_output(
                ["/usr/bin/dpkg", "-L", packagename])
        except OSError:
            return None

        lines = output.decode('utf8').split(os.linesep)
        if filename_regex is not None:
            lines = [x for x in lines if re.match(filename_regex, x)]
        return lines

    @staticmethod
    def list_alternatives(name):
        try:
            output = subprocess.check_output(
                ["/usr/bin/update-alternatives", "--list", name])
            return output.decode('utf8').split(os.linesep)
        except OSError:
            return None

    @staticmethod
    def get_file_package(filename):
        try:
            output = subprocess.check_output(["/usr/bin/dpkg", "-S", filename])

            lines = output.decode('utf8').split(os.linesep)
            if len(lines) < 1:
                return None

            # now, line contains something like "openjdk-7-jre-headless:amd64:
            # /usr/lib/... "
            line = str(lines[0]).split(":")
            if len(line) < 1:
                return None
            return line[0]
        except OSError:
            return None

    @staticmethod
    def get_alt_installed_version(name):
        version_info = DebianPackageManager.__get_alternative_version(name)
        if version_info is not None:
            return version_info[1]

    @staticmethod
    def get_alt_upgradeable_version(name):
        version_info = DebianPackageManager.__get_alternative_version(name)
        if version_info is not None:
            return version_info[2]

    @staticmethod
    def __get_alternative_version(name):
        alternatives = DebianPackageManager.list_alternatives(name)
        if alternatives is None:
            return None

        packages = list()
        for alt in [a for a in alternatives if len(a) > 0]:
            pkg = DebianPackageManager.get_file_package(alt)
            if pkg is not None:
                packages.append(pkg)

        for pkg in packages:
            version_info = DebianPackageManager.get_package_upgrade_info(pkg)
            if version_info is not None:
                return version_info
        return None


# pylint: disable=no-member
AbstractPackageManager.register(DebianPackageManager)
