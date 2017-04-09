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

from hardening import core
from hardening.storage import StorageHandler
from hardening.storage.Transaction import Transaction


@StorageHandler("notransaction")
class NoTransaction(Transaction):
    """
    This class is a transaction which does nothing
    it is needed for hardening utils which can not use a transaction, since the program
    architecture requires a transaction object for every change
    """

    def __init__(self, url):
        super(NoTransaction, self).__init__(url)

    def inform_user(self, message=""):
        pass

    def __begin__(self):
        core.LogManager().get_logger().info(
            _("this transaction will not create any backups!!!"))

    def __commit__(self):
        pass

    def __prepare_commit__(self):
        pass

    def __rollback__(self):
        pass


# pylint: disable=no-member
Transaction.register(NoTransaction)
