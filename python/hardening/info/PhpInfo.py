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
from hardening.info.lib import PackageManager
from hardening.core import singleton
from hardening import io


@singleton
@InfoHandler("php")
class PhpInfo(object):
    """
    provides information about the currently installed php environment
    """

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.__php_ini = "/etc/php5/fpm/php.ini"

        if not os.path.exists(self.__php_ini):
            self.__php_ini = "/etc/php5/php.ini"

            if not os.path.exists(self.__php_ini):
                self.__php_ini = None

    def get_php_ini(self):
        """returns the absolute path of the global php configuration file.

        Currently, we simply return `/etc/php5/fpm/php.ini`
        """
        if self.__php_ini is None:
            self.__php_ini = io.create_writer().prompt_user_input(message=_(
                "Please specify the full path to your PHP 'php.ini' file. "
                "This is by default located at '/etc/php5/php.ini' or '/etc/php5/fpm/php.ini' "
                "but was not found there."))

        return "file:" + self.__php_ini

    @staticmethod
    def get_current_version(*_):
        return PackageManager().get_package_manager().get_alt_upgradeable_version("php")
