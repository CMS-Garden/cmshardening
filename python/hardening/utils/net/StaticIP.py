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

import socket
import struct

from hardening import utils, constants, storage


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_INTERFACE,
                         required=True,
                         docstring="name of the interface to be configured"),
        utils.UtilOption(constants.OPTION_INETADDRESS,
                         required=True,
                         docstring="IPv4 network address"),
        utils.UtilOption(constants.OPTION_NETMASK, required=False,
                         docstring="subnet mask, defaults to 255.255.255.0"),
        utils.UtilOption(constants.OPTION_GATEWAY, required=False,
                         docstring="IPv4 address of the default gateay, if any")
    ],
    required_transaction=storage.NetworkInterfacesTransaction
)
class StaticIP(utils.HardeningUtil):
    """
    uses the current network configuration, no matter if its being configured statically or
    dynamically, and writes a network configuration file, so that the current configuration is
    static from now on. No dhcp will be used afterwards
    """

    def __init__(self, **kwargs):
        super(StaticIP, self).__init__(**kwargs)

    def __run__(self):
        interface = self.get_option(constants.OPTION_INTERFACE)

        address = self.get_option(constants.OPTION_INETADDRESS)
        netmask = self.get_option(
            constants.OPTION_NETMASK, default_value="255.255.255.0")

        self.transaction()[interface].startup = "auto " + interface
        self.transaction()[interface].address_family = "inet"
        self.transaction()[interface].method = "static"
        self.transaction()[interface].address = address
        self.transaction()[interface].netmask = netmask

        gateway = self.get_option(constants.OPTION_GATEWAY, default_value=None)
        if gateway is not None and self.is_in_same_subnet(
                gateway, address, netmask):
            self.transaction()[interface].gateway = gateway

    @staticmethod
    def is_in_same_subnet(ip_address1, ip_address2, subnet):
        ip_address1 = StaticIP.dotted_quad_to_num(ip_address1)
        ip_address2 = StaticIP.dotted_quad_to_num(ip_address2)
        subnet = StaticIP.dotted_quad_to_num(subnet)

        return (ip_address1 & subnet) == (ip_address2 & subnet)

    @staticmethod
    def dotted_quad_to_num(ip_str):
        return struct.unpack('>L', socket.inet_aton(ip_str))[0]
