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

from datetime import datetime
import os
import tempfile

from hardening import info
from hardening.core import singleton
from hardening.core import RuntimeOptions


@singleton
class TransactionInfo(object):
    """
    helper class holding information that needs to be consistent through all transactions
    """

    def __init__(self):
        self.__timestamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
        self.__dirname = os.path.join(info.Configuration().get_property(
            "Backup", "BaseDir", default=tempfile.gettempdir()), self.__timestamp)

    def get_timestamp(self):
        return self.__timestamp

    def get_backupdir(self, subdir=None):
        if subdir is None:
            dirname = self.__dirname
        else:
            dirname = os.path.join(self.__dirname, *subdir.split(os.sep))

        if not os.path.exists(dirname):
            mode = info.Configuration().get_property(
                "Backup", "BaseDirMode", default=0o700)
            if not RuntimeOptions().pretend_mode():
                os.makedirs(dirname, mode)
        return dirname
