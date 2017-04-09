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


# pylint: disable=too-few-public-methods
class StorageHandler(object):
    """
    class to register the type of the transaction
    e.g. xml for .xml files
    """

    def __init__(self, url_schema):
        self.__url_schema = url_schema

    def __call__(self, cls):
        cls.url_schema = staticmethod(lambda: self.__url_schema)
        TransactionManager().register_storage_handler(self.__url_schema, cls)
        return cls


# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.Transaction import Transaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.TransactionInfo import TransactionInfo

# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening import core


@core.singleton
class TransactionManager(object):
    """
    class managing all transaction objects
    has functions to create specific transaction and commit or rollback all active transactions
    """

    def __init__(self):
        self.__transactions = list()
        self.__transaction_index = dict()
        self.__transaction_classes = dict()

    def register_storage_handler(self, url_schema, cls):
        assert url_schema not in self.__transaction_classes
        self.__transaction_classes[url_schema] = cls

    def commit_all(self):
        for transaction in self.__transactions:
            transaction.prepare_commit()

        for transaction in self.__transactions:
            transaction.commit()

    def rollback_all(self):
        if not self.__transactions:
            return
        if len(self.__transactions) == 0:
            return

        for transaction in reversed(self.__transactions):
            transaction.rollback()

    def create_transaction(self, url, **kwargs):
        if url is None:
            url = "notransaction:acknuo4aw784zrpyonsuircpywl4u38oxw8m49u8w30mp0a48uw3p984xuawop"

        if url not in self.__transaction_index:

            schema, address = self.parse_url(url)
            core.LogManager().get_logger().debug("creating transaction for '%(address)s'"
                                                 % {'address': address})

            if schema not in self.__transaction_classes.keys():
                raise SyntaxError(
                    _("invalid schema for transaction: %(schema)s")
                    % {'schema': schema})

            transaction = self.__transaction_classes[schema](address, **kwargs)

            assert transaction not in self.__transaction_index.values()
            self.__transaction_index[url] = transaction

            assert transaction not in self.__transactions
            self.__transactions.append(transaction)

        else:
            core.LogManager().get_logger().debug("using existing transaction for '%(url)s'"
                                                 % {'url': url})

        return self.__transaction_index[url]

    def parse_url(self, url):
        parts = url.split(':')
        if parts is None or len(parts) < 2:
            raise SyntaxError(
                _("invalid url syntax: %(url)s")
                % {'url': url})

        schema = parts[0]
        address = ":".join(parts[1:])
        if schema is None or schema not in self.__transaction_classes.keys():
            raise SyntaxError(
                _("invalid schema for transaction: %(schema)s")
                % {'schema': schema})

        return schema, address


# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.CommandTransaction import CommandTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.DirectoryTransaction import DirectoryTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.FileAndDirectoryTransaction import FileAndDirectoryTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.FileTransaction import FileTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.MysqlTransaction import MysqlTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.NoTransaction import NoTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.TextFileTransaction import TextFileTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.XmlTransaction import XmlTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.PasswdTransaction import PasswdTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.ServiceTransaction import ServiceTransaction
# noinspection PyPep8
# pylint: disable=wrong-import-position
from hardening.storage.NetworkInterfacesTransaction import NetworkInterfacesTransaction
