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

from hardening.info import InfoHandler
from hardening.info.lib import NetworkConfiguration


@InfoHandler("net")
class NetInfo(object):
    """
    provides information about the current networking configuration
    """

    @staticmethod
    def get_interfaces(*_):
        """returns the names of all network interfaces (excluding `lo`)"""
        return NetworkConfiguration().get_interfaces()

    @staticmethod
    def get_interface(index, *_):
        """returns the name of the interface with the given `index`"""
        return list(NetworkConfiguration().get_interfaces().keys())[int(index)]

    def get_inet_address(self, index, *_):
        """returns the ip address of the interface with the given `index`"""
        return self.get_interface_info(index, 'addr')

    def get_netmask(self, index, *_):
        """returns the subnet mask of the interface with the given `index`"""
        return self.get_interface_info(index, 'netmask')

    @staticmethod
    def get_interface_info(index, infoname):
        """returns some specific information of the interface with the given `index`

        Supported values for `infoname` are `addr`, `netmask` and `peer`
        """
        interface = list(NetworkConfiguration().get_interfaces().keys())[
            int(index)]
        addr = NetworkConfiguration().get_interfaces()[interface]
        return addr[0][infoname]

    @staticmethod
    def get_gateway(index):
        """returns the gateway ip address of the interface with the given `index`"""
        gateway = NetworkConfiguration().get_default_gw()
        if gateway[1] == list(NetworkConfiguration().get_interfaces().keys())[
                int(index)]:
            return gateway[0]
        else:
            return None

    @staticmethod
    def get_nameservers():
        """returns a list of ip addresses, representing name servers"""
        return NetworkConfiguration().get_nameservers()

    @staticmethod
    def get_resolv_conf(*_):
        """returns the current DNS configuration"""
        return NetworkConfiguration().get_resolv_conf()

    @staticmethod
    def get_static_addresses(*_):
        """returns a list of all ip addresses (excluding `127.0.0.1`)"""
        return NetworkConfiguration().get_static_addresses()

    @staticmethod
    def get_management_address(*_):
        """returns the IP address which shall be used by management services, such as SSH"""
        return NetworkConfiguration().get_management_address()

    @staticmethod
    def get_public_address(*_):
        """returns the IP address which shall be used by services which are publicly available"""
        return NetworkConfiguration().get_public_address()

    @staticmethod
    def get_default_gw(*_):
        """returns the IP address of the default gateway"""
        return NetworkConfiguration().get_default_gw()
