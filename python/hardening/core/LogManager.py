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

import logging
import os
import inspect
import yaml

from hardening import constants
from hardening.core.RuntimeOptions import RuntimeOptions
from hardening.core.Singleton import singleton
from hardening.core.caller_name import caller_name

try:
    from coloredlogs import ColoredFormatter as HardeningFormatter
except ImportError:
    # pylint: disable=ungrouped-imports
    from logging import Formatter as HardeningFormatter

LOGLEVEL_DEFAULT = logging.DEBUG
DefaultLogHandlerClass = logging.StreamHandler

CONFIG_FILENAME = 'config.yml'


@singleton
class LogManager(object):
    """
    handles access to a log sink, such as the console or a log file, and provides transparent
    access to it. The caller does not need to know the currently configured destination, severity,
    etc.
    """

    def __init__(self):
        self.__loggers = {}

        config_file = os.path.join(
            RuntimeOptions().base_path(), constants.FILENAME_GLOBALCONFIG)

        with open(config_file, 'r') as stream:
            stream_content = stream.read(-1)
            config = yaml.load(stream_content)

        self.__loglevel = LOGLEVEL_DEFAULT
        self.__loghandler = DefaultLogHandlerClass
        if constants.CONFIG_LOGGING in config.keys():
            log_config = config[constants.CONFIG_LOGGING]

            if constants.CONFIG_LOGLEVEL in log_config:
                self.__loglevel = getattr(
                    logging, log_config[constants.CONFIG_LOGLEVEL])

            if constants.CONFIG_LOGHANDLER in log_config:
                self.__loghandler = getattr(
                    logging, log_config[constants.CONFIG_LOGHANDLER])

    def get_loglevel(self):
        return self.__loglevel

    def get_loghandler(self):
        loghandler = self.__loghandler()
        loghandler.setFormatter(HardeningFormatter(self.get_logformat()))
        return loghandler

    @staticmethod
    def get_logformat():
        return "%(asctime)s %(name)s: %(message)s"

    def get_logger(self, name=None):
        if name is None and len(inspect.stack()) > 1:
            name = caller_name().split(".")[-2]

        if name not in self.__loggers:
            self.__loggers[name] = logging.getLogger(name)
            self.__loggers[name].setLevel(self.get_loglevel())
            self.__loggers[name].addHandler(self.get_loghandler())
        return self.__loggers[name]
