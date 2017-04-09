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
from hardening.core.RuntimeOptions import RuntimeOptions
from hardening.core.Singleton import singleton


@singleton
class ChangeLog(object):
    """Provides a way to document which changes have been made to the current system

    This class simply wraps a Singleton around a list, to which entries can be added. Because this
    is a Singleton, you should never store a reference a core.ChangeLog object
    """

    def __init__(self):
        self.__items = list()

    def append_log_item(self, *items):
        """append lines to the change log

        If the lines to be added do not end with a newline (we use os.linesep), then one will be
        appended
        @param items: one or more items to be added to the changecore. All items will be converted
        to string before they are appended.
        """
        for item in [str(x) for x in items]:
            if not item.endswith(os.linesep):
                item = item + os.linesep
            self.__items.append(item)

    def get_log_as_string(self):
        """creates a string representation of the whole change log

        @return the change log as string
        """
        return os.linesep.join(self.__items)

    def store_log(self):
        """stores the current change log

        At the moment, the whole changelog is written to stdout. This should be changed later so
        that the destination can be configured
        """
        RuntimeOptions().logfile().writelines(self.__items)

    def has_items_to_save(self):
        """
        return whether or not there is some content in the log
        """
        return len(self.__items) > 0
