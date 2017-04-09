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

import subprocess
import os
from hardening import info, core
from hardening.info import lib as info_lib


@info.InfoHandler("condition")
class Condition(object):
    """
    Condition is used to make decisions based on configuration details. Each method in this returns
    a boolean which is True when the condition described by the name of the method is true.
    E.g. Condition::get_has_package_installed() can be called by using
    `info:condition:has_package_installed:<your_package_name>` in the yaml files and returns
    True if `<your_package_name>` is installed
    """

    def __init__(self):
        if info_lib.OSInfo().distribution_name().lower().startswith("debian"):
            self.__package_manager = info_lib.DebianPackageManager()
        else:
            self.__package_manager = None

    @staticmethod
    def get_not(*args):
        return not info.Info().interpolate("condition:" + ":".join(args))

    def get_has_package_installed(self, package, *_):
        """returns `True` if `package` is installed on the local system"""
        return self.__package_manager.is_package_installed(package)

    @staticmethod
    def get_hardening_for_wordpress(*_):
        """returns `True` if the configuration must be tailored for Wordpress
        """
        return core.RuntimeOptions().content_management_system == "wordpress"

    @staticmethod
    def get_hardening_for_joomla(*_):
        """returns `True` if the configuration must be tailored for Joomla
        """
        return core.RuntimeOptions().content_management_system == "joomla"

    @staticmethod
    def get_hardening_for_plone(*_):
        """returns `True` if the configuration must be tailored for Plone
        """
        return core.RuntimeOptions().content_management_system == "plone"

    @staticmethod
    def get_hardening_for_liferay(*_):
        """returns `True` if the configuration must be tailored for Liferay
        """
        return core.RuntimeOptions().content_management_system == "liferay"

    @staticmethod
    def get_hardening_for_typo3(*_):
        """returns `True` if the configuration must be tailored for Typo3
        """
        return core.RuntimeOptions().content_management_system == "typo3"

    def get_has_php_installed(self, *_):
        """returns `True` if PHP (php-fpm) is installed
        """
        if self.__package_manager is None:
            return False

        return self.__package_manager.is_package_installed("php5-fpm")

    def get_has_apache_installed(self, *_):
        """returns `True` if Apache (apache2) is installed
        """
        if self.__package_manager is None:
            return False

        return self.__package_manager.is_package_installed("apache2")

    @staticmethod
    def get_has_sshd_config(*_):
        return os.path.isfile("/etc/ssh/sshd_config")

    @staticmethod
    def get_has_network_interface(index, *_):
        """returns `True` if a specific interface exists.

        All network interfaces are internally indexed, starting with `0`; the interfaces `lo` is
        omitted. So, the first interfaces may be externally reachable has the index `0`
        """
        return info_lib.NetworkConfiguration().has_interface(index=int(index))

    @staticmethod
    def get_has_service(svcname):
        process = subprocess.Popen(["/bin/systemctl",
                                    "is-enabled",
                                    svcname,
                                    "--quiet"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        process.communicate()
        if process.returncode != 0:
            return False
        else:
            return True

    @staticmethod
    def get_true(*_):
        """evaluates to `True`
        """
        return True

    @staticmethod
    def get_false(*_):
        """evaluates to `False`
        """
