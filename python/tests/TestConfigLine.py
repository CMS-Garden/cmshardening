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
from hardening.utils.configfile import ConfigLine


class TestConfigLine(unittest.TestCase):
    """
    Tests the CongifLine implementation for different key-value-seperator tuples as well as for
    list objects
    """

    def test_equals1(self):
        a = ConfigLine(key="mykey", value="myvalue", listseparator=None)
        b = ConfigLine(key="mykey", value="myvalue", listseparator=None)
        self.assertEquals(a, b)

    def test_equals2(self):
        a = ConfigLine(key="mykey", value=[
                       "value1", "value2"], listseparator=None)
        b = ConfigLine(key="mykey", value=[
                       "value2", "value1"], listseparator=None)
        self.assertEquals(a, b)

    def test_equals3(self):
        a = ConfigLine(key="Ciphers", value=["aes256-ctr",
                                             "aes128-gcm@openssh.com",
                                             "aes128-ctr",
                                             "chacha20-poly1305@openssh.com",
                                             "aes256-gcm@openssh.com",
                                             "aes192-ctr"], listseparator=",")
        b_txt = "Ciphers aes256-ctr,chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr," \
                "aes128-gcm@openssh.com,aes256-gcm@openssh.com\n"
        b = a.match_old_line(b_txt)
        c = b.merge(a)
        self.assertEquals(a, c)

    def test_notequals1(self):
        a = ConfigLine(key="mykey", value="myvalue1", listseparator=None)
        b = ConfigLine(key="mykey", value="myvalue2", listseparator=None)
        self.assertNotEquals(a, b)

    def test_notequals_none1(self):
        a = ConfigLine(key="mykey", value=None, listseparator=None)
        b = ConfigLine(key="mykey", value="myvalue2", listseparator=None)
        self.assertNotEquals(a, b)

    def test_notequals_none2(self):
        a = ConfigLine(key="mykey", value="myvalue1", listseparator=None)
        b = ConfigLine(key="mykey", value=None, listseparator=None)
        self.assertNotEquals(a, b)

    def test_merge1(self):
        a = ConfigLine(key="mykey", value="myvalue",
                       listseparator=None, separator="=")
        b = ConfigLine(key="mykey", value="myvalue",
                       listseparator=None, separator="=")
        c = a.merge(b)
        d = "mykey=myvalue"
        self.assertEquals(d, str(c))

    def test_merge2(self):
        a = ConfigLine(key="mykey", value="myvalue1",
                       listseparator=None, separator="=")
        b = ConfigLine(key="mykey", value="myvalue2",
                       listseparator=None, separator="=")
        c = a.merge(b)
        d = "mykey=myvalue1"
        self.assertEquals(d, str(c))

    def test_merge3(self):
        a = ConfigLine(key="mykey", value="myvalue1",
                       listseparator=",", separator="=")
        b = ConfigLine(key="mykey", value="myvalue2",
                       listseparator=",", separator="=")
        c = a.merge(b)
        d = "mykey=myvalue2,myvalue1"
        self.assertEquals(d, str(c))


if __name__ == '__main__':
    unittest.main()
