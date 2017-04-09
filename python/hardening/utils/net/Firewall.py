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

from hardening import utils, storage, constants
from hardening.info.lib import NetworkConfiguration


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_PROTOCOL, required=True,
                         docstring="name of the protocol. must be either `tcp`, `udp` or `icmp`"),
        utils.UtilOption(constants.OPTION_SRC, required=False,
                         docstring="name or ip address of the sending host"),
        utils.UtilOption(constants.OPTION_DST, required=False,
                         docstring="name of ip address of the receiving host"),
        utils.UtilOption(constants.OPTION_ACTION, required=False,
                         docstring="specifies what shoud be done with matching packets. "
                                   "Default value is `ACCEPT`"),
        utils.UtilOption(constants.OPTION_CHAIN, required=False,
                         docstring="name of the chain where the rule must be inserted. "
                                   "Should be `INPUT`, `OUTPUT` or `FORWARD`"),
        utils.UtilOption(constants.OPTION_SRCPORT, required=False,
                         docstring="source port of the packet. Only valid for `tcp` and `udp`"),
        utils.UtilOption(constants.OPTION_DSTPORT, required=False,
                         docstring="destination port of the packet. "
                                   "Only valid for `tcp` and `udp`"),
        utils.UtilOption(constants.OPTION_ICMPTYPE, required=False,
                         docstring="ICMP type. Please run `iptables -p icmp -h` "
                                   "to see which values are supported on your system")
    ],
    required_transaction=storage.TextFileTransaction,
    required_packages=["netfilter-persistent", "iptables-persistent"])
# pylint: disable=too-many-instance-attributes
class Firewall(utils.HardeningUtil):
    """
    creates a firewall rule. Be aware that the default policy for all chains is "DROP", which cannot
     be altered using configuration files
    """

    FILTER_REGEX = r'^\*filter\s*'
    INPUT_REGEX = r'^:INPUT\s+DROP(\s.*)?'
    FORWARD_REGEX = r'^:FORWARD\s+DROP(\s.*)?'
    OUTPUT_REGEX = r'^:OUTPUT\s+DROP(\s.*)?'

    def __init__(self, **kwargs):
        super(Firewall, self).__init__(**kwargs)

        self.__src = None
        self.__dst = None
        self.__action = None
        self.__chain = None
        self.__config = list()

        self.__srcport = None
        self.__dstport = None
        self.__icmptype = None

        self.__configline = None

    def __setup__(self):

        self.__src = self.get_option(constants.OPTION_SRC, "0.0.0.0/0")
        self.__dst = self.get_option(constants.OPTION_DST, "0.0.0.0/0")
        assert self.__src is not None and self.__dst is not None

        self.__action = self.get_option(constants.OPTION_ACTION, 'ACCEPT')
        self.__chain = self.get_option(constants.OPTION_CHAIN)

        if self.__chain is None:
            if self.__src in NetworkConfiguration().get_static_addresses():
                self.__chain = 'OUTPUT'
            elif self.__dst in NetworkConfiguration().get_static_addresses():
                self.__chain = 'INPUT'
            else:
                raise SyntaxError(_("invalid ip address in firewall rule"))

        self.__config.extend(["-A", self.__chain])
        self.__config.extend(["-s", self.__src])
        self.__config.extend(["-d", self.__dst])
        self.__config.extend(
            ["-p", self.get_str_option(constants.OPTION_PROTOCOL).lower()])

        if self.get_str_option(constants.OPTION_PROTOCOL).lower() == "tcp":
            self.__setup_tcp_udp("tcp")

            self.__config.extend(["-m", "conntrack"])
            self.__config.extend(["--ctstate", "NEW"])

        elif self.get_str_option(constants.OPTION_PROTOCOL).lower() == "udp":
            self.__setup_tcp_udp("udp")
        elif self.get_str_option(constants.OPTION_PROTOCOL).lower() == "icmp":
            self.__setup_icmp()
        else:
            raise SyntaxError(_("invalid protocol specified: '%(protocol)s'")
                              % {'protocol': self.get_option(constants.OPTION_PROTOCOL)})

        self.__config.extend(["--jump", self.__action])
        self.__configline = " ".join(self.__config)

    def __setup_tcp_udp(self, protocol="tcp"):
        self.__srcport = self.get_option(constants.OPTION_SRCPORT)
        self.__dstport = self.get_option(constants.OPTION_DSTPORT)

        self.__config.extend(["-m", protocol])
        if self.__srcport is not None:
            self.__config.extend(["--sport", str(self.__srcport)])
        if self.__dstport is not None:
            self.__config.extend(["--dport", str(self.__dstport)])

    def __setup_icmp(self):
        self.__icmptype = self.get_option(constants.OPTION_ICMPTYPE)
        self.__config.extend(["--icmp-type", self.__icmptype])

    def __run__(self):

        self.transaction().insert_unique_line(0, "*filter", silent=True,
                                              regex=Firewall.FILTER_REGEX)
        self.transaction().insert_unique_line(1, ":INPUT DROP [0:0]", silent=True,
                                              regex=Firewall.INPUT_REGEX)
        self.transaction().insert_unique_line(2, ":FORWARD DROP [0:0]", silent=True,
                                              regex=Firewall.FORWARD_REGEX)
        self.transaction().insert_unique_line(3, ":OUTPUT DROP [0:0]", silent=True,
                                              regex=Firewall.OUTPUT_REGEX)

        input_idx = self.transaction().find_line_by_regex(regex=Firewall.INPUT_REGEX)
        forward_idx = self.transaction().find_line_by_regex(regex=Firewall.FORWARD_REGEX)
        output_idx = self.transaction().find_line_by_regex(regex=Firewall.OUTPUT_REGEX)
        filter_idx = self.transaction().find_line_by_regex(regex=Firewall.FILTER_REGEX)

        idx = max(output_idx, forward_idx, input_idx, filter_idx)

        initial_rules = (
            # permit packets belonging to existing connections
            "-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
            "-A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",

            # drop invalid packet state
            "-A INPUT -m conntrack --ctstate INVALID -j DROP",
            "-A OUTPUT -m conntrack --ctstate INVALID -j DROP",

            # allow all loopback connection
            "-A INPUT -i lo -j ACCEPT",
            "-A OUTPUT -o lo -j ACCEPT"
        )

        for k in range(0, len(initial_rules)):
            self.transaction().insert_unique_line(idx + k, initial_rules[k])

        try:
            idx = self.transaction().index("COMMIT")
            self.transaction().insert_unique_line(idx, self.__configline)
        except ValueError:
            self.transaction().append_unique_line(self.__configline)
            self.transaction().append_line("COMMIT", silent=True)
