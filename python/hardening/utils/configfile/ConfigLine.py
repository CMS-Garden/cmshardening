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

from hardening import core


# pylint: disable=too-many-instance-attributes
class ConfigLine(object):
    """
    helper object representing a single line within a configuration file
    support several functions like comparing,merging or adding key-separator-values tuples
    """

    def __init__(self, key, value, separator=" ", listseparator=None, commentchar="#", indent="",
                 multiple=False):
        self.__key = key
        self.__value = value
        self.__separator = separator
        self.__listseparator = listseparator
        self.__commentchar = commentchar
        self.__indent = indent
        self.__line_regex = re.compile(self.__create_line_regex())
        self.__iscommented = False
        self.__multiple = multiple

    def __str__(self):
        if isinstance(self.__value, list):
            self.__value = self.__listseparator.join(self.__value)
        return "%s%s%s" % (self.__key, self.__separator, self.__value)

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        return self.__value

    @property
    def separator(self):
        return self.__separator

    @property
    def listseparator(self):
        return self.__listseparator

    @property
    def commentchar(self):
        return self.__commentchar

    @property
    def iscommented(self):
        return self.__iscommented

    @iscommented.setter
    def iscommented(self, is_commented):
        self.__iscommented = is_commented

    @property
    def indent(self):
        return self.__indent

    @indent.setter
    def indent(self, value):
        self.__indent = value

    @staticmethod
    def safe_strip(str_value):
        if str_value is None:
            return str_value
        if isinstance(str_value, str):
            return str_value.strip()
        return str_value

    def safe_compare(self, str_value1, str_value2):
        if (str_value1 is None) != (str_value2 is None):
            core.LogManager().get_logger().debug("comparing to None")
            return False
        if str_value1 is None:
            return True
        if isinstance(str_value1, list) and isinstance(str_value2, str):
            core.LogManager().get_logger().debug("comparing list and string")
            str_value1 = self.__listseparator.join(str_value1)
        if isinstance(str_value1, list) and isinstance(str_value2, list):
            str_value1 = set(str_value1)
            str_value2 = set(str_value2)
        return str_value1 == str_value2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.safe_compare(self.key, other.key) and \
            self.safe_compare(self.value, other.value) and \
            self.safe_compare(self.separator, other.separator) and \
            self.safe_compare(self.listseparator, other.listseparator) and \
            self.safe_compare(self.commentchar, other.commentchar)

    def __create_line_regex(self):
        whitespace = re.compile(r"^\s+$")

        if whitespace.match(self.separator):
            regex = r"\A(?P<indent>\s*)(?P<commentchar>(?:" + \
                    re.escape(self.__commentchar) + r")?)\s*" + \
                    re.escape(self.__key) + r"(?:" + \
                    r"\b\s*" + re.escape(self.__separator) + r"|" + \
                    r"\s*" + re.escape(self.__separator) + r")\s*" + \
                    r"(?P<value>[^" + re.escape(self.__commentchar) + "]*)"
        else:
            regex = r"\A(?P<indent>\s*)(?P<commentchar>(?:" + \
                    re.escape(self.__commentchar) + r")?)\s*" + \
                    re.escape(self.__key) + r"(?:" + \
                    r"\b\s*" + re.escape(self.__separator) + r"|" + \
                    r"\s+" + re.escape(self.__separator) + r")\s*" + \
                    r"(?P<value>[^" + re.escape(self.__commentchar) + "]*)"
        return regex

    def match_old_line(self, line):
        line = line.rstrip("\n")
        result = self.__line_regex.match(line)
        if result:
            if self.__listseparator is None:
                value = result.group('value')
            else:
                value = result.group('value').split(self.__listseparator)
            indent = result.group('indent')
            oldline = ConfigLine(key=self.__key,
                                 value=value,
                                 separator=self.__separator,
                                 listseparator=self.__listseparator,
                                 commentchar=self.__commentchar,
                                 indent=indent)

            if len(result.group('commentchar')) > 0:
                oldline.iscommented = True

            return oldline
        else:
            return None

    def merge(self, other):
        if other is not None:
            assert self.__key == other.key
            assert self.__separator == other.separator
            assert self.__listseparator == other.listseparator
            assert self.__commentchar == other.commentchar

        return ConfigLine(
            key=self.__key,
            value=self.__create_new_value(other),
            separator=self.__separator,
            listseparator=self.__listseparator,
            commentchar=self.__commentchar,
            indent=max(self.__indent, other.indent, key=len)
        )

    def __create_new_value(self, oldline):

        if isinstance(self.value, list) and self.listseparator is None:
            raise SyntaxError(_("missing list separator"))

        if self.listseparator is not None:
            if oldline is None:
                oldlist = set()

            elif isinstance(oldline.value, list):
                oldlist = set(oldline.value)
            else:
                oldlist = set(oldline.value.split(self.listseparator))

            if isinstance(self.value, list):
                selflist = set(self.value)
            else:
                selflist = set(self.value.split(self.listseparator))

            newlist = oldlist.union(selflist)
            new_value = list(newlist)
        else:
            new_value = self.value

        return new_value
