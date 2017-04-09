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
from hardening import utils, constants, storage, core
from hardening.utils.configfile.ConfigFileEntry import ConfigFileEntry


# pylint: disable=duplicate-code
@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_TRANSACTION, required=True,
                         docstring="path of the apache config file"),
        utils.UtilOption(constants.OPTION_KEY, required=True,
                         docstring="name of the configuration setting"),
        utils.UtilOption(constants.OPTION_VALUE, required=True,
                         docstring="value to be set for the configuration setting"),
        utils.UtilOption(constants.OPTION_SECTION, required=False,
                         docstring="section inside the config file where "
                                   "setting must be placed in"),
        utils.UtilOption(constants.OPTION_LISTSEPARATOR, required=False,
                         docstring="if the value is a list then this options specifies "
                                   "how the distinct values must be separated"),
        utils.UtilOption(constants.OPTION_SEPARATOR, required=False,
                         docstring="the string that divides setting name and setting "
                                   "value in the config file"),
        utils.UtilOption(constants.OPTION_COMMENTCHAR, required=False,
                         docstring="all characters in a line after the comment "
                                   "character are ignored"),
        utils.UtilOption(constants.OPTION_MULTIPLE, required=False,
                         docstring="if this is set to true then existing settings with the "
                                   "same key and different value are not overwritten, "
                                   "but a new line is being inserted"),
        utils.UtilOption(constants.OPTION_BEFOREKEY, required=False,
                         docstring="describes a key in the config file BEFORE which the "
                                   "current setting will be inserted.")
    ],
    required_transaction=storage.TextFileTransaction)
class ApacheConfigEntry(ConfigFileEntry):
    """
    ApacheConfigEntry is a specialized version of ConfigFileEntry which is able to find a specific
    section inside the config file and put the requested value into this section
    """

    def __init__(self, **kwargs):
        super(ApacheConfigEntry, self).__init__(**kwargs)
        self.__section = None
        self.__enter_section = None
        self.__leave_section = None

    def __setup__(self):
        ConfigFileEntry.__setup__(self)
        self.__section = self.get_option(constants.OPTION_SECTION)
        self.__enter_section = re.compile(
            r'\s*<([^\s]+)\s+"?([^">]+)"?\s*>\s*$')
        self.__leave_section = re.compile(r'\s*</([^\s]+)\s*>\s*$')

        if self.__section is not None:
            if 'name' not in self.__section or 'param' not in self.__section:
                raise SyntaxError("missing value in section description")
            if self.__section['name'] is None or len(
                    self.__section['name'].strip()) == 0:
                self.__section = None

    def __find_section(self):
        section_stack = list()

        section_start = None
        section_end = None

        idx = 0
        while idx < self.transaction().lines_count():

            result_begin = self.__enter_section.match(
                self.transaction().line(idx))
            result_end = self.__leave_section.match(
                self.transaction().line(idx))

            if result_begin:
                section_start = self.handle_section_begin(idx, result_begin, section_stack,
                                                          section_start)
            elif result_end:
                section_end = self.handle_section_end(idx, result_end, section_end, section_stack,
                                                      section_start)
                if section_start is not None and section_end is not None:
                    return section_start, section_end
            idx += 1

        # we did not find the section we searched for, so we create it at the
        # end of the file
        self.__create_missing_section()
        return idx, idx + 1

    def handle_section_begin(self, idx, result_begin,
                             section_stack, section_start):
        section_stack.append(
            {'name': result_begin.group(1), 'param': result_begin.group(2)})
        core.LogManager().get_logger().debug(
            "entering " + str(section_stack[-1]))
        if self.current_sctn_is_target_sctn(section_stack):
            if section_start is None:
                section_start = idx
            else:
                raise SyntaxError("invalid apache config file")
        return section_start

    def handle_section_end(self, idx, result_end,
                           section_end, section_stack, section_start):
        if len(section_stack) == 0:
            raise SyntaxError("invalid apache config file")
        current_section = section_stack[-1]
        core.LogManager().get_logger().debug("leaving " + str(current_section))
        if current_section['name'] != result_end.group(1):
            raise SyntaxError("invalid apache config file")
        if self.current_sctn_is_target_sctn(section_stack):
            if section_end is None and section_start is not None:
                section_end = idx
            else:
                raise SyntaxError("invalid apache config file")

        del section_stack[-1]
        return section_end

    def __create_missing_section(self):
        self.transaction().append_line("", True)
        self.transaction().append_line(self.__create_section_begin(), True)
        self.transaction().append_line(self.__create_section_end(), True)
        core.LogManager().get_logger().info(
            _("requested section '%(name)s %(param)s' not found. Creating section.")
            % {'name': self.__section['name'], 'param': self.__section['param']})

    def current_sctn_is_target_sctn(self, section_stack):
        if self.__section is None and len(section_stack) > 0:
            return False
        if self.__section is not None and len(section_stack) == 0:
            return False
        if self.__section is not None and self.__section != section_stack[-1]:
            return False
        return True

    def __create_section_begin(self):
        if self.__section is None:
            return None
        return '<%s "%s">' % (self.__section['name'], self.__section['param'])

    def __create_section_end(self):
        if self.__section is None:
            return None
        return '</%s>' % self.__section['name']

    def __section_start_index(self):
        return self.__find_section()[0]

    def __section_end_index(self):
        return self.__find_section()[1]

    def get_minimum_index(self):
        if self.__section is None:
            return 0
        else:
            return self.__section_start_index()

    def get_maximum_index(self):
        if self.__section is None:
            return self.transaction().lines_count() - 1
        else:
            return self.__section_end_index()

    def get_nesting_level(self):
        return 1
