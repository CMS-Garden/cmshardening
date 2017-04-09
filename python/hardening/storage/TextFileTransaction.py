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

import difflib
import copy
import os
import re
from hardening import core, io
from hardening.storage import StorageHandler
from hardening.storage.FileTransaction import FileTransaction


@StorageHandler("file")
class TextFileTransaction(FileTransaction):
    """
    Transaction class for simple text files  allowing modifications and storing of changes for
    this file type
    """

    def __init__(self, filename):
        super(TextFileTransaction, self).__init__(filename)
        self.__lines = None
        self.__original_lines = None
        self.__delete_file = False
        self.__apply_changes = None
        self.__configline_indent = "    "

    def __begin__(self):
        """
        read all lines in one list, which can be manipulated easily as long as
        the config file is line-based
        """

        FileTransaction.__begin__(self)

        self.__lines = [x.rstrip(os.linesep) for x in self.readlines()]
        self.__original_lines = copy.copy(self.__lines)

    def __prepare_commit__(self):
        if core.RuntimeOptions().is_log_enabled():
            diff = list(
                difflib.unified_diff(self.__original_lines, self.__lines, self.tmpname(),
                                     self.url()))
            if len(diff) > 0:
                self.append_to_changelog(
                    "###########################################")
                self.append_to_changelog("patch '%s' <<EOF" % self.url())
                self.append_to_changelog(*diff)
                self.append_to_changelog("EOF")

        super(TextFileTransaction, self).__prepare_commit__()

    def new_file_content(self):
        # append os.linesep to be POSIX-conform
        # (http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap03.html#tag_03_206)
        if len(self.__lines) == 0:
            return ""
        else:
            return os.linesep.join(self.__lines) + os.linesep

    def must_apply_changes(self):
        if core.RuntimeOptions().pretend_mode():
            return False

        if core.RuntimeOptions().difference_mode() and self.has_modifications_to_save():
            diff = list(difflib.unified_diff(
                self.__original_lines, self.__lines))

            # be aware: we cannot use self.prompt_user here, because this method expects a
            # HardeningUtil-instance somewhere on the stack. But must_apply_changes is called
            # during Transaction.commit(); i.e. after all HardeningUtils have
            # been run
            if len(diff) > 0 and \
                    not io.create_writer().prompt_user_yesnocancel(
                            _("Do you want to apply the following changes to '%(filename)s'")
                            % {'filename': self.url()}, quoted=diff):
                return False
        return self.has_modifications_to_save()

    def line(self, index):
        return self.__lines[index]

    def lines_count(self):
        return len(self.__lines)

    def append_line(self, line, silent=False):
        assert self.is_transaction_running()
        assert isinstance(line, str)
        assert "\n" not in line
        if not silent and core.RuntimeOptions().interactive_mode():
            if not self.prompt_user(
                    _("Do you want to append the following line to '%(filename)s'?\n\n"
                      "%(indent)s%(line)s\n")
                    % {'filename': self.url(),
                       'indent': self.__configline_indent,
                       'line': str.strip(line)}):
                return
        self.__lines.append(line)
        self.mark_as_modified()

    def index(self, item):
        return self.__lines.index(item)

    def append_unique_line(self, line):
        assert self.is_transaction_running()
        if line not in self.__lines:
            self.append_line(line)

    def insert_unique_line(self, idx, line, silent=False, regex=None):
        assert self.is_transaction_running()
        if regex is None:
            if line not in self.__lines:
                self.insert_line(idx, line, silent=silent)
        else:
            line_regex = re.compile(regex)
            assert line_regex.match(line)
            for current_line in self.__lines:
                if line_regex.match(current_line):
                    return
            self.insert_line(idx, line, silent=silent)

    def find_line_by_regex(self, regex):
        line_regex = re.compile(regex)
        for idx in range(0, len(self.__lines)):
            if line_regex.match(self.__lines[idx]):
                return idx
        raise ValueError()

    def delete_line(self, index):
        assert self.is_transaction_running()
        if core.RuntimeOptions().interactive_mode():
            if not self.prompt_user(
                    _("Do you want to delete the following line from "
                      "'%(filename)s'?\n\n%(indent)s%(line)s\n")
                    % {'filename': self.url(),
                       'indent': self.__configline_indent,
                       'line': self.__lines[index]}):
                return
        del self.__lines[index]
        self.mark_as_modified()

    def insert_line(self, index, line, silent=False):
        assert self.is_transaction_running()
        assert isinstance(line, str)
        if not silent and core.RuntimeOptions().interactive_mode():
            if not self.prompt_user(
                    _("Do you want to insert the following line to "
                      "'%(filename)s'?\n\n%(indent)s%(line)s\n")
                    % {'filename': self.url(),
                       'indent': self.__configline_indent,
                       'line': str.strip(line)}):
                return
        self.__lines.insert(index, line)
        self.mark_as_modified()

    def set_line(self, index, line):
        assert self.is_transaction_running()
        assert self.__lines[index] != line
        if core.RuntimeOptions().interactive_mode():
            if not self.prompt_user(
                    _("Do you want to replace the following line"
                      "\n\n%(indent)s%(oldline)s\n\nby\n\n%(indent)s%(newline)s"
                      "\nin '%(filename)s'?")
                    % {'oldline': self.__lines[index].strip(),
                       'newline': str.strip(line),
                       'indent': self.__configline_indent,
                       'filename': self.url()}):
                return
        self.__lines[index] = line
        self.mark_as_modified()

    def flush(self):
        assert self.is_transaction_running()
        self.__lines = list()
        self.mark_as_modified()

    def add_lines(self, *lines):
        assert self.is_transaction_running()
        if core.RuntimeOptions().interactive_mode():
            if not self.prompt_user(
                    _("Do you want to append the following lines to '%(filename)s'?\n")
                    % {'filename': self.url()}, quoted=lines):
                return

        self.__lines.extend(lines)

        if len(lines) > 0:
            self.mark_as_modified()


# pylint: disable=no-member
FileTransaction.register(TextFileTransaction)
