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

# -*- coding: utf-8 -*-
import os
import sys
import six

from hardening import io, core


class ConsoleWriter(io.Writer):
    """
    Implementation of io::Writer which is capable to write to the system console
    """
    LINE_LENGTH = 79
    HEADLINE_PREFIX = "| "
    HEADLINE_INTRO = "+" + "=" * 79
    HEADLINE_OUTRO = "+" + "=" * 79

    QUOTED_INTRO = "+" + "-" * 79
    QUOTED_OUTRO = QUOTED_INTRO
    QUOTED_PREFIX = "> "

    def __init__(self):
        io.Writer.__init__(self)

        # pylint: disable=no-member
        if sys.version_info[0] < 3:
            self.__writer = sys.stdout
        else:
            self.__writer = sys.stdout.buffer

    def __console_write(self, message):
        self.__writer.write(message.encode(sys.stdout.encoding, errors="replace"))

    @staticmethod
    def __getch():
        import tty
        import termios
        file_no = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_no)
        try:
            tty.setraw(sys.stdin.fileno())
            character = sys.stdin.read(1)
        finally:
            termios.tcsetattr(file_no, termios.TCSADRAIN, old_settings)
        return character

    def __write(self, message, hint=None, end=": ", begin=""):
        output = ''
        output += begin
        output += message

        if hint is not None:
            output += "[" + hint + "]"
        output += end

        self.__console_write(output)
        sys.stdout.flush()

    @staticmethod
    def raw_input():
        return six.moves.input()

    def prompt_user_yesno(self, message, default=_("yes"), **kwargs):
        __user_input = None
        hint = None

        if default is not None:
            default = default.lower()
            if _("yes").startswith(default):
                hint = _("(Y)ES/(n)o")
            elif _("no").startswith(default):
                hint = _("(yes)/(N)O")
            else:
                raise RuntimeError(_("invalid default value"))

        while __user_input is None:
            self.write_message(description=message, hint=hint, **kwargs)

            inp = self.__getch()
            if len(inp) == 0 or ord(inp) == 10 or ord(inp) == 13:
                if default is None:
                    continue
                inp = default

            self.__console_write(inp[:1] + os.linesep)
            inp = inp.lower()
            if _("yes").startswith(inp):
                __user_input = True
            elif _("no").startswith(inp):
                __user_input = False

        return __user_input

    def prompt_user_yesnocancel(
            self, message="", default=_("yes"), *args, **kwargs):
        __user_input = None
        hint = _("(Y)es/(N)o/(C)ancel")

        if default is not None:
            default = default.lower()
            if _("yes").startswith(default):
                hint = _("(Y)ES/(n)o/(c)ancel")
            elif _("no").startswith(default):
                hint = _("(yes)/(N)O/(c)ancel")
            elif _("cancel").startswith(default):
                hint = _("(y)es/(n)o/(C)CANCEL")

        while __user_input is None:
            self.write_message(message=message, hint=hint, *args, **kwargs)

            inp = self.__getch()
            if len(inp) == 0 or ord(inp) == 10 or ord(inp) == 13:
                if default is None:
                    continue
                inp = default

            self.__console_write(inp[:1] + os.linesep)
            inp = inp.lower()
            if _("yes").startswith(inp):
                __user_input = True
            elif _("no").startswith(inp):
                __user_input = False
            elif _("cancel").startswith(inp):
                sys.exit(0)

        return __user_input

    def prompt_user_input(self, message="", validator=None, default=None):
        __user_input = None

        while __user_input is None:
            self.write_message(message=message + ": ", hint=default)
            __user_input = six.moves.input().strip()

            if validator is not None:
                if not validator(__user_input):
                    self.__console_write(_("Your input isn't valid"))
                    __user_input = None

        return __user_input

    def prompt_to_choose(self, message, values=None, allow_userinput=False):
        if values is None:
            values = []
        __user_input = None

        while __user_input is None:
            self.__console_write(message.strip() + ":\n")
            digits = len(str(len(values)))

            for idx, value in enumerate(values):
                self.__console_write(
                    ("  [%" + str(digits) + "d] %s\n") % (idx, value))

            self.__console_write(_("Your value: "))
            inp = six.moves.input()
            try:
                index = int(inp)
                if 0 <= index < len(values):
                    __user_input = values[index]
            except ValueError:
                if allow_userinput or inp in values:
                    __user_input = inp
        return __user_input

    def write_message(self, message=None, property_name=None, hint=None, caption=None, quoted=None,
                      description=None):

        self.display_message(description, caption)
        self.__write("", end="\n")

        if message is not None:
            self.__write(message, end="\n")
        elif property_name is not None:
            assert property_name != ''
            self.__write(_("Please insert value for property '%(property)s'")
                         % {'property': property_name})

        if quoted is not None:
            self.display_quoted_lines(*quoted)
        if hint is not None:
            self.__write("", hint=hint)

    def display_quoted_lines(self, *lines):
        self.__write(self.QUOTED_INTRO, end="\n")
        for line in lines:
            if line.endswith("\n"):
                line = line[:-1]
            self.__write(self.QUOTED_PREFIX + line, end="\n")
        self.__write(self.QUOTED_OUTRO, end="\n")

    def display_message(self, message, headline=None, hyphenate=True):

        if headline is not None:
            self.display_headline(headline)

        if message is not None:

            message = self.replace_special_whitespace(message)
            if hyphenate:
                for line in self.hyphenate_string(message, self.LINE_LENGTH):
                    self.__write(line, end="\n")
            else:
                self.__write(message, end="\n")

    def display_headline(self, headline):
        headline = self.replace_special_whitespace(headline)

        if core.ExecutionState().current_module is not None:
            headline = "%s: %s" % (
                core.ExecutionState().current_module, headline)

        self.__write(self.HEADLINE_INTRO, end="\n", begin="\n")
        for line in self.hyphenate_string(
                headline, self.LINE_LENGTH - len(self.HEADLINE_PREFIX)):
            self.__write(self.HEADLINE_PREFIX + line, end="\n")
        self.__write(self.HEADLINE_OUTRO, end="\n")

    @staticmethod
    def replace_special_whitespace(text):
        return text.replace(u'\u00a7{n}', os.linesep).replace(
            u'\u00a7{t}', "\t")

    @staticmethod
    def hyphenate_string(text, line_length):
        text = text.replace("\r", "")

        result = list()

        for text in text.splitlines():
            while len(text) > line_length:
                idx = text[:line_length].rindex(" ")
                result.append(text[:idx])
                text = text[idx + 1:]
            result.append(text)
        return result


# pylint: disable=no-member
io.Writer.register(ConsoleWriter)
