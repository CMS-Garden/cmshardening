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
from hardening import storage
from hardening.storage.Transaction import TransactionStatus


class TestTransactionStates(unittest.TestCase):
    """
    Tests the different transaction states and their transitions
    """

    def setUp(self):
        self.__transaction = storage.NoTransaction(self.__class__.__name__)

    def transaction(self):
        return self.__transaction

    def testSimpleStates(self):
        self.assertEquals(self.transaction().status(), TransactionStatus.NEW)
        self.assertFalse(self.transaction().is_transaction_running())

        self.transaction().begin()
        self.assertEquals(self.transaction().status(),
                          TransactionStatus.RUNNING)
        self.assertTrue(self.transaction().is_transaction_running())

        self.transaction().prepare_commit()
        self.assertEquals(self.transaction().status(),
                          TransactionStatus.COMMITPREPARED)
        self.assertFalse(self.transaction().is_transaction_running())

        self.transaction().commit()
        self.assertEquals(self.transaction().status(),
                          TransactionStatus.COMMITTED)
        self.assertFalse(self.transaction().is_transaction_running())

        # with self.assertRaises(RuntimeError):
        #    self.transaction().rollback()
