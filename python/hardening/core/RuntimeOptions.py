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

import argparse
import inspect
import os
import sys
from datetime import datetime

import locale

# noinspection PyBroadException
try:
    # noinspection PyShadowingBuiltins,PyUnresolvedReferences
    # pylint: disable=redefined-builtin
    import itertools.filter as filter
except ImportError:
    pass

from hardening.core.Singleton import singleton
import hardening

MODE_INTERACTIVE = 'interactive'
MODE_DIFFERENCE = 'diff'
MODE_SILENT = 'silent'
MODE_PRETEND = 'check-only'

ARGUMENT_MODE = 'mode'
ARGUMENT_LANG = 'lang'
ARGUMENT_LOG = 'log'
ARGUMENT_DOCUMENTATION = 'documentation'


@singleton
class RuntimeOptions(object):
    # noinspection PyPep8
    # pylint: disable=line-too-long
    """provides access to runtime options.

            Runtime options define the way in which the hardening scripts shall work and my define additional options, such
            as logfile location, debug mode, log verbosity and so on. At the moment, the term 'runtime options' refers to
            command line arguments, which may change later when the script is invoked by some other management software.

            Be aware that this is a Singleton. You should not store a reference to a core.RuntimeOptions object!

            Currently the following options are supported:
            | Option | Command line switch | Meaning |
            | ------ | ------------------- | ------- |
            | Interactive Mode | `--mode=interactive` | In Interactive mode, every change to a configuration and the execution of any (hardening) command must be confirmed by the user. There may be some commands which run without user confirmation, such as `apache2ctl` to determine apache build options. But command which alter the systems configuration must be confirmed in this mode.|
            | Difference Mode | `--mode=diff` | In contrast to the interactive mode, not every change to configuration file is confirmed in this mode. Instead, a (unified) difference between the original and the altered version of the file is displayed and must be confirmed by the user. The user has the choice between all and nothing when using this mode. |
            | Pretend Mode | `--mode=check-only` | When the scripts run in pretend mode, no changed will be made at all. This mode is useful when combined with the Logging mode |
            | Logging | `--log` | All changes to the system will be written to the core::ChangeLog::ChangeLog. This output can be redirected to a file and run later as script.  |
            """

    def __init__(self):
        self.__language_code = None
        self.__parser = argparse.ArgumentParser(prog=hardening.__programname__)
        self.__parser.add_argument("--mode",
                                   dest=ARGUMENT_MODE,
                                   choices=[MODE_INTERACTIVE, MODE_DIFFERENCE, MODE_SILENT,
                                            MODE_PRETEND],
                                   default=MODE_PRETEND,
                                   help="Select the mode in which this script will run. "
                                        "Default is " + MODE_PRETEND)
        self.__parser.add_argument("--lang",
                                   dest=ARGUMENT_LANG,
                                   help="Select language for this tool. Default is your system "
                                        "locale or english. Valid options are de_DE (or only 'de') "
                                        "and en_US (or only 'en').")
        self.__parser.add_argument("--log",
                                   dest=ARGUMENT_LOG,
                                   metavar='logfile',
                                   help="Display a log of applied changes; "
                                        "you can use '-' as filename to log to stdout")
        self.__parser.add_argument("--version",
                                   action='version',
                                   help="Display the version of this tool.",
                                   version='%(prog)s ' + hardening.__version__)
        self.__parser.add_argument("--documentation",
                                   dest=ARGUMENT_DOCUMENTATION,
                                   action='store_const',
                                   const=True,
                                   help="Display the full documentation in markdown format.")
        self.__args = vars(self.__parser.parse_args())

        if "help" in self.__args.keys() or "version" in self.__args.keys():
            sys.exit(0)

        self.__parge_language()
        self.__parse_log()

        self.__mode = self.__args[ARGUMENT_MODE]
        self.__cms = None

    def __parse_log(self):
        if ARGUMENT_LOG in self.__args.keys():
            if self.__args[ARGUMENT_LOG] is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
                root_dir = os.path.expanduser("~")
                self.__logfile = open(os.path.join(
                    root_dir, "hardening_%s.log" % timestamp), 'w')
            elif self.__args[ARGUMENT_LOG] == '-':
                self.__logfile = sys.stdout
            else:
                try:
                    self.__logfile = open(self.__args[ARGUMENT_LOG], "w")
                except IOError:
                    self.__parser.error("invalid filename: '%s'" %
                                        self.__args[ARGUMENT_LOG])
                    sys.exit(-1)
        else:
            self.__logfile = None

    def __parge_language(self):
        if ARGUMENT_LANG in self.__args.keys() and self.__args[ARGUMENT_LANG] is not None:
            # get locales directory
            available_locales_directory = os.path.abspath(os.path.join(os.path.dirname(
                inspect.getfile(inspect.currentframe())), os.pardir, os.pardir, "locale"))
            # get available locales
            available_locales = [d for d in os.listdir(available_locales_directory) if
                                 os.path.isdir(os.path.join(available_locales_directory, d))]

            # if argument in locales return argument
            if self.__args[ARGUMENT_LANG] in available_locales:
                self.__language_code = self.__args[ARGUMENT_LANG]

            # if argument not in locales, split argument and try to find locale
            # containing the argument
            elif self.__args[ARGUMENT_LANG].split('_')[0] in [l.split("_")[0] for l in
                                                              available_locales]:
                filtered_locale = \
                    filter(lambda l: self.__args[ARGUMENT_LANG].split('_')[0] in l.split("_")[0],
                           available_locales)
                try:
                    self.__language_code = filtered_locale[0]
                except TypeError:
                    self.__language_code = next(filtered_locale)
            else:
                self.__language_code = "en_US"
        else:
            self.__language_code, _ = locale.getdefaultlocale()

    def logfile(self):
        """returns a handle to a logfile, or None if no logfile was specified"""
        return self.__logfile

    @staticmethod
    def base_path():
        """ determines the parent directory of RuntimeOptions::lib_path.

        This information is used by several other classes in order to find YAML files,
        InfoHandler and so on. Normally, the base path is the directory in which the main python
        file is located

        @return absolute path of the base directory as string
        """
        return os.path.abspath(
            os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), os.pardir,
                         os.pardir))

    @staticmethod
    def lib_path():
        """ determines which directory on the local system this whole software is stored.

        This information is used by several other classes in order to find YAML files, InfoHandler
        and so on. Normally, the base path is the directory in which the main python file is located

        @return absolute path of the base directory as string
        """
        return os.path.abspath(
            os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), os.pardir))

    def difference_mode(self):
        """ determines if difference mode is activated

        @return `True` if difference mode is active; `False` otherwise
        """
        return self.__mode == MODE_DIFFERENCE

    def interactive_mode(self):
        """ determines if interactive mode is activated

        @return `True` if interactive mode is active; `False` otherwise
        """
        return self.__mode == MODE_INTERACTIVE

    def silent_mode(self):
        """ determines if silent mode is activated

        @return `True` if silent mode is active; `False` otherwise
        """
        return self.__mode == MODE_SILENT

    def enable_silent_mode(self):
        """ enables the silent mode

        """
        self.__mode = MODE_SILENT

    def pretend_mode(self):
        """ determines if pretend mode is activated

        @return `True` if pretend mode is active; `False` otherwise
        """
        return self.__mode == MODE_PRETEND

    def is_log_enabled(self):
        """ determines if logging is enabled

        @return `True` if logging is enabled; `False` otherwise
        """
        return self.__logfile is not None

    def is_documentation_enabled(self):
        return ARGUMENT_DOCUMENTATION in self.__args.keys() and \
            self.__args[ARGUMENT_DOCUMENTATION]

    def get_locale(self):
        if self.__language_code is None:
            self.__language_code = "en_US"

        return self.__language_code

    def get_help_text(self):
        return self.__parser.format_help()

    @property
    def content_management_system(self):
        return self.__cms

    @content_management_system.setter
    def content_management_system(self, cms):
        self.__cms = cms
