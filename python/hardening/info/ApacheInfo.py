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
from hardening.info.lib import ApacheConfig

SSL_CONFIG_NAME = "ssl.conf"
SECURITY_CONFIG_NAME = "security.conf"
APACHE_CONFIG_NAME = "apache2.conf"


@InfoHandler("apache")
class ApacheInfo(object):
    """
    ApacheInfo is responsible for providing configuration details of the current apache installation
    """

    @staticmethod
    def get_ssl_config(*_):
        """returns the absolute path of the local `ssl_config` file

        Normally, the path should be `/etc/apache2/mods-available/ssl_config` in Debian Linux
        """
        configpath = "mods-available"
        return "file:" + os.path.join(ApacheConfig().get_httpd_root(),
                                      configpath, SSL_CONFIG_NAME)

    @staticmethod
    def get_security_config(*_):
        """returns the absolute path of the local `security.conf` file

        Normally, the path should be `/etc/apache2/conf-available/security.conf` in Debian Linux
        """
        configpath = "conf-available"
        return "file:" + os.path.join(ApacheConfig().get_httpd_root(),
                                      configpath, SECURITY_CONFIG_NAME)

    @staticmethod
    def get_apache_config(*_):
        """returns the absolute path of the local `apache2.conf` file

        Normally, the path should be `/etc/apache2/apache2.conf` in Debian Linux
        """
        return "file:" + os.path.join(ApacheConfig().get_httpd_root(),
                                      APACHE_CONFIG_NAME)
