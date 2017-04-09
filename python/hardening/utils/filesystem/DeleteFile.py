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

from hardening import utils, storage


@utils.ModuleSettings(
    required_transaction=storage.FileAndDirectoryTransaction)
class DeleteFile(utils.HardeningUtil):
    """
    this class can be used to delete a file from the filesystem. wildcards for filenames are
    currently not supported
    """

    def __run__(self):
        self.transaction().delete()
