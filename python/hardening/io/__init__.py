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

import importlib
import sys
from abc import ABCMeta, abstractmethod

from six import with_metaclass

WRITER_CLASS = "ConsoleWriter"


def create_writer():
    writer_class = WRITER_CLASS
    module_name = "%s.%s.%s" % ("hardening", "io", writer_class)
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        module = importlib.import_module(module_name)
    cls = getattr(module, writer_class)

    return cls()


class Writer(with_metaclass(ABCMeta)):
    """
    Writer connects the hardening scripts with user input: The user can be prompted for input,
    which is than returned to the program. The output may be simply text-based (console) or
    even web-based.
    """

    def __init__(self):
        pass

    @abstractmethod
    def display_message(self, message, headline=None, hyphenate=True):
        pass

    @abstractmethod
    def prompt_user_yesno(self, *args, **kwargs):
        pass

    @abstractmethod
    def prompt_user_yesnocancel(self, *args, **kwargs):
        pass

    @abstractmethod
    def prompt_user_input(self, message="", validator=None, default=None):
        pass

    @abstractmethod
    def prompt_to_choose(self, message, values=None, allow_userinput=False):
        pass
