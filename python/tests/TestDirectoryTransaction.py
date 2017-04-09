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

import unittest
import tempfile
import os
import stat
import shutil
from hardening.storage import DirectoryTransaction
from hardening.core import RuntimeOptions


class TestDirectoryTransactionTestCase(unittest.TestCase):
    """
    Tests directory transaction functions like chmod on directories
    """

    def testRollback1(self):
        self.transaction().chmod(0o777)

        self.assertTrue(os.path.exists(self.transaction().tmpname()))
        self.transaction().rollback()
        self.assertFalse(os.path.exists(self.transaction().tmpname()))

    def testChmod1(self):
        new_mode = 0o741
        self.transaction().chmod(new_mode)

        # make sure the new settings have been applied to the temporary
        # directory
        current_mode = os.stat(self.transaction().tmpname()).st_mode
        self.assertEqual(new_mode, stat.S_IMODE(current_mode))

        # the new settings should not apply to the current directory yet
        current_mode = os.stat(self.transaction().url()).st_mode
        self.assertNotEqual(new_mode, stat.S_IMODE(current_mode))

        self.transaction().prepare_commit()
        current_mode = os.stat(self.transaction().url()).st_mode
        self.assertNotEqual(new_mode, stat.S_IMODE(current_mode))

        self.assertTrue(os.path.exists(self.transaction().tmpname()))
        self.transaction().commit()
        self.assertFalse(os.path.exists(self.transaction().tmpname()))

        current_mode = os.stat(self.transaction().url()).st_mode
        self.assertEqual(new_mode, stat.S_IMODE(current_mode))

    def testChmod2(self):
        new_user_mode = "a=rwx"
        new_group_mode = "g-wx"
        new_world_mode = "o-rwx"
        desired_mode = 0o740
        self.transaction().chmod(new_user_mode)
        self.transaction().chmod(new_group_mode)
        self.transaction().chmod(new_world_mode)

        self.transaction().prepare_commit()
        self.transaction().commit()
        current_mode = os.stat(self.transaction().url()).st_mode
        self.assertEqual(desired_mode, stat.S_IMODE(current_mode))

    def setUp(self):
        RuntimeOptions().enable_silent_mode()
        origdir = tempfile.mkdtemp()
        self.__filename = origdir
        self.__transaction = DirectoryTransaction(self.__filename)
        self.__transaction.begin()

    def tearDown(self):
        self.__transaction = None
        if os.path.exists(self.filename()):
            shutil.rmtree(self.filename())

    def transaction(self):
        return self.__transaction

    def filename(self):
        return self.__filename
