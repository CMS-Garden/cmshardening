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
import re
import subprocess

from hardening import core


@core.singleton
class ApacheConfig(object):
    # noinspection PyPep8
    # pylint: disable=line-too-long
    """Provides several information about the installed apache package.

        | Method | Information | Information source |
        | ------ | ----------- | ------------------ |
        | ApacheConfig::get_version | Server version | Output of ``apache2ctl``, value of ``Server version`` |
        | ApacheConfig::get_httpd_root | Directory where apache configuration files are located | ``configure``-setting ``HTTPD_ROOT``, obtained using ``apache2ctl`` |
        | ApacheConfig::get_server_configfile | absolute path of apache configuration file, usually ``/etc/apache2/apache2.conf``| ``configure``-setting ``SERVER_CONFIG_FILE``, obtained using ``apache2ctl`` |

        """

    def __init__(self):
        self.__configdir = "/etc/apache2"
        self.__envvars = os.path.join(self.__configdir, "envvars")
        self.__versioninfo = None

    def get_version(self):
        """ returns the version of the apache server

        @return server version as string
        """
        self.__read_apache_version()
        return self.__versioninfo['Server version']

    def get_httpd_root(self):
        """ returns the configuration root directory (`HTTPD_ROOT`) of the apache server

        @return directory name as string
        """
        self.__read_apache_version()
        return self.__versioninfo['HTTPD_ROOT']

    def get_server_configfile(self):
        """ returns the path of apaches configuration file (`SERVER_CONFIG_FILE`)

        @return file path as string
        """
        self.__read_apache_version()
        return self.__versioninfo['SERVER_CONFIG_FILE']

    def get_enabled_modules(self):
        """returns a list of all enabled modules
        """
        enabled_modules_path = os.path.join(
            self.get_httpd_root(), "mods-enabled")
        modules = list()
        for _, _, files in os.walk(enabled_modules_path):
            modules.extend([x[:-5] for x in files if x.endswith(".load")])
        return modules

    def __read_apache_version(self):
        if self.__versioninfo is not None:
            return

        self.__versioninfo = dict()
        regex_genericinfo = re.compile(r"^\s*([^:]+):\s*(.*)$")
        regex_compiledwith = re.compile(r'\s*-D\s+([^=]+)(?:="?([^"]*)"?)?')

        cmd = self.__get_apache_command(params=["-V"])
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            core.LogManager().get_logger().fatal(stderr.strip())
            raise subprocess.CalledProcessError(
                process.returncode, cmd, output=stderr)

        for line in stdout.split(b"\n"):
            result = regex_genericinfo.match(line.decode('utf-8'))
            if result:
                self.__versioninfo[result.group(1)] = result.group(2)
                continue

            result = regex_compiledwith.match(line.decode('utf-8'))
            if result:
                self.__versioninfo[result.group(1)] = result.group(2)
                continue

    @staticmethod
    def __get_apache_command(apache_envvars="/etc/apache2/envvars",
                             apache_confdir=None,
                             apachectl='/usr/sbin/apache2ctl',
                             params=None):
        if params is None:
            params = []
        command = ["/usr/bin/env", "-i", "LANG=C",
                   "PATH=/usr/sbin:/usr/bin:/sbin:/bin"]

        if apache_envvars is not None:
            command.append("APACHE_ENVVARS=%s" % apache_envvars)

        if apache_confdir is not None:
            command.append("APACHE_CONFDIR=%s" % apache_confdir)

        command.append(apachectl)
        command.extend(params)
        return command
