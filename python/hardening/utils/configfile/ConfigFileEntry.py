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

import ast
import six

from hardening.utils.configfile.ConfigLine import ConfigLine
from hardening import core, storage, constants, utils, info


# pylint: disable=duplicate-code
@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_TRANSACTION, required=True,
                         docstring="path of the config file"),
        utils.UtilOption(constants.OPTION_KEY, required=True,
                         docstring="name of the configuration setting"),
        utils.UtilOption(constants.OPTION_VALUE, required=True,
                         docstring="value to be set for the configuration setting"),
        utils.UtilOption(constants.OPTION_SEPARATOR, required=False,
                         docstring="the string that divides setting name and setting "
                                   "value in the config file"),
        utils.UtilOption(constants.OPTION_LISTSEPARATOR, required=False,
                         docstring="if the value is a list then this options specifies "
                                   "how the distinct values must be separated"),
        utils.UtilOption(constants.OPTION_COMMENTCHAR, required=False,
                         docstring="all characters in a line after the comment character "
                                   "are ignored"),
        utils.UtilOption(constants.OPTION_MULTIPLE, required=False,
                         docstring="if this is set to true then existing settings with the "
                                   "same key and different value are not overwritten, "
                                   " a new line is being inserted"),
        utils.UtilOption(constants.OPTION_BEFOREKEY, required=False,
                         docstring="describes a key in the config file BEFORE which the "
                                   "current setting will be inserted.")
    ],
    required_transaction=storage.TextFileTransaction)
class ConfigFileEntry(utils.HardeningUtil):
    """
    searches through the given configuration file if there already exists a setting whose name
    matches that of the given key. If a matching entry is found, it is being updated. If no matching
    entry is found, the setting will be appended to the file. If the user has set `multiple` to
    `True`, than also the value will be used to find a matching value. This allows to add multiple
    settings with the same key, but different value, to a file.
    """

    def __init__(self, **kwargs):
        super(ConfigFileEntry, self).__init__(**kwargs)
        self.__newline = None
        self.__multiple = None
        self.__nextline = None

    def __setup__(self):
        try:
            self.__multiple = ast.literal_eval(
                self.get_option(constants.OPTION_MULTIPLE, "False").capitalize())
        except ValueError:
            core.LogManager().get_logger().fatal(
                _("invalid value for 'multiple': '%s'") %
                self.get_option(constants.OPTION_MULTIPLE))
            raise

        self.__newline = ConfigLine(
            key=self.get_option(constants.OPTION_KEY),
            value=self.get_option(constants.OPTION_VALUE),
            separator=self.get_option(constants.OPTION_SEPARATOR,
                                      default_value=self.get_default_separator()),
            listseparator=self.get_option(
                key=constants.OPTION_LISTSEPARATOR, default_value=None),
            commentchar=self.get_option(key=constants.OPTION_COMMENTCHAR,
                                        default_value=self.get_default_commentchar()),
            multiple=self.__multiple)

        self.__nextline = None
        if self.get_option(constants.OPTION_BEFOREKEY) is not None:
            self.__nextline = ConfigLine(
                key=self.get_option(constants.OPTION_BEFOREKEY),
                value="",
                separator=self.get_option(constants.OPTION_SEPARATOR,
                                          default_value=self.get_default_separator()),
                listseparator=self.get_option(
                    key=constants.OPTION_LISTSEPARATOR,
                    default_value=None),
                commentchar=self.get_option(
                    key=constants.OPTION_COMMENTCHAR,
                    default_value=self.get_default_commentchar()))

    # pylint: disable=no-self-use
    def get_default_separator(self):
        return ' '

    # pylint: disable=no-self-use
    def get_default_commentchar(self):
        return "#"

    def find_matching_lines(self, line, minpos, maxpos):
        lines = dict()

        if minpos is None:
            minpos = 0

        if maxpos is None:
            maxpos = self.transaction().lines_count() - 1

        for idx in range(minpos, maxpos + 1):
            oldline = line.match_old_line(self.transaction().line(idx))
            if oldline:
                lines[idx] = oldline
        return lines

    def __run__(self):
        minpos = self.get_minimum_index()
        maxpos = self.get_maximum_index()

        # None means that there is no restriction
        assert minpos is None or maxpos is None or minpos <= maxpos
        oldlines = self.find_matching_lines(self.__newline, minpos, maxpos)

        # no lines to be updated, so insert new line at the end of the allowed
        # section
        if len(oldlines) == 0:
            if maxpos is None:
                self.transaction().append_line(self.__format_line(self.__newline))
            else:
                self.transaction().insert_line(maxpos, self.__format_line(self.__newline))
            return

        if self.__multiple:
            if maxpos is None:
                maxpos = self.transaction().lines_count() - 1
            self.insert_multiple(oldlines, maxpos)
        else:
            self.insert_unique(oldlines)

    @staticmethod
    def first_line_index(oldlines):
        _min = six.MAXSIZE
        for idx in oldlines.keys():
            if idx < _min:
                _min = idx

        if _min == six.MAXSIZE:
            return None
        else:
            return _min

    @staticmethod
    def last_line_index(oldlines):
        _max = -1
        for idx in oldlines.keys():
            if idx > _max:
                _max = idx

        if _max == -1:
            return None
        else:
            return _max

    def insert_multiple(self, oldlines, maxpos):
        # check if the new line already exists; if yes, don't insert it
        if self.__newline in oldlines.values():
            self.transaction().inform_user(
                message=_(
                    "value of '%(key)s' in '%(filename)s' is already up to date")
                % {'key': self.get_option(constants.OPTION_KEY),
                   'filename': self.transaction().url()})
            return

        if maxpos == -1:  # empty file
            self.transaction().append_line(self.__format_line(self.__newline))
        else:
            self.transaction().insert_line(maxpos, self.__format_line(self.__newline))

    def __format_line(self, line):
        if self.get_nesting_level() < 1:
            return self.__newline.indent + str(line)
        else:
            return info.Configuration().get_property(
                constants.CONFIG_TEXTFILES,
                constants.CONFIG_DEFAULTINDENT,
                default_value=str("    ") * self.get_nesting_level()) + str(line)

    def insert_unique(self, oldlines):
        uncommented = {k: v for k, v in six.iteritems(
            oldlines) if not v.iscommented}

        if len(uncommented) > 1:
            # perhaps this key should have 'multiple' set?
            raise SyntaxError(
                _("configuration setting has occured multiple times: '%(key)s' in %(filename)s")
                % {'key': self.get_option(constants.OPTION_KEY),
                   'filename': self.transaction().url()})

        # use the first matching line
        if len(uncommented) == 0:
            idx, line = list(oldlines.items())[0]
        else:
            idx, line = list(uncommented.items())[0]

        if line.iscommented:
            core.LogManager().get_logger().debug(
                _("%(key)s in %(filename)s: calling insert_line()")
                % {'key': self.get_option(constants.OPTION_KEY),
                   'filename': self.transaction().url()})
            self.transaction().insert_line(idx + 1, self.__format_line(self.__newline))
            return

        newline = self.__newline.merge(line)
        if line != newline:
            core.LogManager().get_logger().debug(
                _("%(key)s in %(filename)s: calling set_line()")
                % {'key': self.get_option(constants.OPTION_KEY),
                   'filename': self.transaction().url()})
            self.transaction().set_line(idx, self.__format_line(newline))
        else:
            if isinstance(newline.value, list):
                self.transaction().inform_user(
                    message=_("values of '%(key)s' in '%(filename)s' are already up to date") %
                    {'key': newline.key, 'filename': self.transaction().url()})
            else:
                self.transaction().inform_user(
                    message=_("value '%(key)s%(separator)s%(value)s' in '%(filename)s'"
                              " is already up to date") %
                    {
                        'key': newline.key,
                        'separator': newline.separator,
                        'value': newline.value,
                        'filename': self.transaction().url()})

    # pylint: disable=no-self-use
    def get_minimum_index(self):
        return None

    def get_maximum_index(self):
        if self.__nextline is not None:
            nextlines = self.find_matching_lines(self.__nextline, 0,
                                                 self.transaction().lines_count() - 1)
            return self.first_line_index(nextlines)
        else:
            return None

    # pylint: disable=no-self-use
    def get_nesting_level(self):
        return 0

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__,
                           self.get_option(constants.OPTION_KEY))
