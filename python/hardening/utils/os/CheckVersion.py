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
import hardening.info.lib as info
from hardening import utils, constants, io


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_KEY, required=True,
                         docstring="specifies which version you are interested "
                                   "in must be one of `php`, `java` or `python`"),
        utils.UtilOption(constants.OPTION_VERSION, required=True,
                         docstring="specifies a version with which the installed version "
                                   "should be compared")
    ],
    required_packages=["aptitude"])
class CheckVersion(utils.HardeningUtil):
    """
    compares the version of an installed component with a version that is specified as parameter
    """

    __KEY_PHP = "php5"
    __KEY_JAVA = "java"
    __KEY_PYTHON = "python"

    __valid_keys = {
        __KEY_PHP: info.PHPConfig(),
        __KEY_JAVA: info.JavaConfig(),
        __KEY_PYTHON: info.PythonConfig()
    }

    def __init__(self, **kwargs):
        super(CheckVersion, self).__init__(**kwargs)
        self.__key = None
        self.__check_version = None
        self.__version = None
        self.__operation = None

    def __setup__(self):

        if self.get_option(
                constants.OPTION_KEY) not in self.__valid_keys.keys():
            raise SyntaxError(_("invalid key for version check: '%(key)s'")
                              % {'key': self.get_option(constants.OPTION_KEY)})
        else:
            self.__key = self.__valid_keys[
                self.get_option(constants.OPTION_KEY)]

        self.__check_version = self.get_str_option(constants.OPTION_VERSION)
        self.__version = self.__key.get_version()

    def __run__(self):
        if self.__version is None or self.__version == "":
            self.__display_message(
                _("It does seems like %(key)s is not installed on your system. "
                  "This isn't a problem if you don't need it but you should consider removing"
                  "the hardening module for %(key)s in the global config.yml.")
                % {'key': self.get_option(constants.OPTION_KEY)})
            return
        else:
            if self.__check_version != self.__version:
                self.__display_message(
                    _("Your %(key)s version is older then '%(version)s'."
                      "You should consider updating it.")
                    % {'key': self.get_option(constants.OPTION_KEY),
                       'version': self.get_option(constants.OPTION_VERSION)})

            else:
                self.__display_message(
                    _("Your %(key)s version is up to date.")
                    % {'key': self.get_option(constants.OPTION_KEY)})

    @staticmethod
    def __display_message(message):
        io.create_writer().display_message(os.linesep)
        io.create_writer().display_message(message)
