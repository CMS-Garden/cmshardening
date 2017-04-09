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

import pwd
import subprocess
import unittest

from hardening import storage, core

TEST_USERNAME = "hardening_test_user"


class PasswdTransactionTestCase(unittest.TestCase):
    """
    Tests passwd operations like adding a user
    """

    def testUseradd(self):
        # the user should already exist
        pwd.getpwnam(TEST_USERNAME)

        self.transaction().prepare_commit()
        self.transaction().commit()

        self.assertIsNotNone(pwd.getpwnam(TEST_USERNAME))

        self.assertEquals(0, subprocess.call(
            ["/usr/sbin/userdel", TEST_USERNAME]))

        with self.assertRaises(KeyError):
            pwd.getpwnam(TEST_USERNAME)

    def setUp(self):
        subprocess.call(["/usr/sbin/userdel", TEST_USERNAME])
        core.RuntimeOptions().enable_silent_mode()
        self.__transaction = storage.PasswdTransaction(TEST_USERNAME)
        self.__transaction.begin()

    def tearDown(self):
        self.__filename = None
        self.__transaction = None

    def transaction(self):
        return self.__transaction
