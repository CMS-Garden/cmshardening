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

import re
import netifaces
from hardening import core, io


@core.singleton
class NetworkConfiguration(object):
    """ provides information about the current networking configuration

    """
    VALID_IP_ADDRESS = re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
                                  r"{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

    def __init__(self):
        self.__interfaces = None
        self.__resolv_conf = dict()
        self.__static_addresses = list()
        self.__management_address = None
        self.__public_address = None
        self.__default_gw = None
        self.__nameservers = None

    def __read_network_configuration(self):
        if self.__interfaces is not None:
            return
        self.__interfaces = dict()

        for interface in netifaces.interfaces():

            # ignore loopback interfaces
            if interface.startswith("lo"):
                continue

            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET not in addrs:
                continue

            self.__interfaces[interface] = addrs[netifaces.AF_INET]
            for addr in addrs[netifaces.AF_INET]:
                self.__static_addresses.append(addr['addr'])
        if len(self.__static_addresses) == 0:
            raise core.HardeningFailure(
                _("This system has no IP addresses configured"))
        elif len(self.__static_addresses) == 1:
            self.__management_address = self.__static_addresses[0]
            self.__public_address = self.__static_addresses[0]
        else:
            self.__management_address = io.create_writer().prompt_to_choose(
                _("Please choose an IP address to be used for MANAGEMENT access"),
                self.__static_addresses
            )
            self.__public_address = io.create_writer().prompt_to_choose(
                _("Please choose an IP address to be used for PUBLIC access"),
                self.__static_addresses
            )
        gws = netifaces.gateways()
        if 'default' in gws:
            self.__default_gw = gws['default'][netifaces.AF_INET]
        resolv_re = re.compile(r"^\s*(domain|search|nameserver)\s+(.*)$")
        with open("/etc/resolv.conf", "r") as resolv_conf:
            for line in resolv_conf:
                match = resolv_re.match(line)
                if match:
                    self.__resolv_conf[match.group(1)] = match.group(2)

    def get_interfaces(self):
        """returns a `list` of interface names

        @return list
        """
        self.__read_network_configuration()
        return self.__interfaces

    def get_resolv_conf(self):
        """returns the current DNS configuration

        @return internal datastructure (a `dict`)
        """
        self.__read_network_configuration()
        return self.__resolv_conf

    def get_nameservers(self):
        if self.__nameservers is None:
            if "nameserver" in self.get_resolv_conf():
                self.__nameservers = self.get_resolv_conf()["nameserver"]
            else:
                self.__nameservers = io.create_writer().prompt_user_input(
                    _("Please type the IP address of your DNS nameserver"),
                    validator=self.VALID_IP_ADDRESS.match)
        return self.__nameservers

    def get_static_addresses(self, interface=None):
        """returns a list of all ip addresses

        @param interface: name of an interface or `None`. if a interface name is specified,
        then all addresses of this interface are returned. If `None` is specified, all addresses
        are returned
        @return list of ip addresses
        """
        self.__read_network_configuration()
        if interface is None:
            return self.__static_addresses
        else:
            return self.__interfaces[interface]

    def get_management_address(self):
        """ returns the ip address to be used for management services
        """
        self.__read_network_configuration()
        return self.__management_address

    def get_public_address(self):
        """ returns the ip address which shall be used for publicly available services
        """
        self.__read_network_configuration()
        return self.__public_address

    def get_default_gw(self):
        """ returns the ip address of the default gateway
        """
        self.__read_network_configuration()
        return self.__default_gw

    def has_interface(self, index=0):
        """ specifies if the given index exists in the list of interfaces

        @param index: index to be requested
        @return `True` iff 0<=index<=len(list of interfaces); `False` otherwise
        """
        self.__read_network_configuration()
        return 0 <= index < len(self.get_interfaces())
