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
from hardening.storage.TextFileTransaction import TextFileTransaction

# use the local network_interfaces clone
import network_interfaces


@StorageHandler("networkconfig")
class NetworkInterfacesTransaction(TextFileTransaction):
    """
    transaction for changes to the network/interfaces file
    this class is a subclass of the TextFileTransaction
    """

    def __init__(self, filename):
        super(NetworkInterfacesTransaction, self).__init__(filename)
        self.__file = network_interfaces.InterfacesFile(filename)

    def __getitem__(self, item):
        try:
            interface = self.__file.get_iface(item)
        except KeyError:
            # we need to set "inet static" explicitely,
            # because Stanza uses unchecked array indexing to set certain
            # values
            interface = network_interfaces.Stanza.create(
                "iface %s inet static" % item, self.url())
            self.__file.add_iface(interface)
            self.mark_as_modified()

        decorator = StanzaDecorator(self, interface)
        return decorator

    def __prepare_commit__(self):
        self.flush()
        for line in self.__file.as_string().split("\n"):
            self.append_line(line, silent=True)
        super(NetworkInterfacesTransaction, self).__prepare_commit__()


class StanzaDecorator(network_interfaces.Stanza):
    """
    this class represents one entry in the network/interfaces file
    """

    # noinspection PyMissingConstructor
    # pylint: disable=super-init-not-called
    def __init__(self, transaction, obj):
        """constructor

        be aware that we do not call the superclass constructor here"""
        self.transaction = transaction
        self.baseobj = obj

    def __setitem__(self, key, value):
        try:
            item = self.get_dict_attr(self.baseobj, key)
            setter = self.baseobj.__setattr__
        except AttributeError:
            setter = self.baseobj.__setitem__
            if key in self.baseobj:
                item = self.baseobj.__getitem__(key)
            else:
                item = None

        if item != value:
            if self.__prompt_user(key, value):
                setter(key, value)
                self.__transaction.mark_as_modified()

    def __getitem__(self, item):
        try:
            return self.get_dict_attr(self.baseobj, item)
        except AttributeError:
            return self.baseobj.__getitem__(item)

    def __setattr__(self, key, value):
        if key in ["transaction", "baseobj"]:
            self.__dict__[key] = value
            return

        if not hasattr(self.baseobj, key) or getattr(
                self.baseobj, key) != value:
            if self.__prompt_user(key, value):
                self.baseobj.__setattr__(key, value)
                self.transaction.mark_as_modified()

    def __getattr__(self, item):
        return getattr(self.baseobj, item)

    def __prompt_user(self, key, value):
        if core.RuntimeOptions().interactive_mode():
            return self.transaction.prompt_user(
                _("Do you want to set '%(key)s' to '%(value)s' for interface %(interface)s?")
                % {'key': key, 'value': value, 'interface': self.baseobj.name})
        return True

    @staticmethod
    def get_dict_attr(obj, attr):
        for obj in [obj] + obj.__class__.mro():
            if attr in obj.__dict__:
                return obj.__dict__[attr]
        raise AttributeError
