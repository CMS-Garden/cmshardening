# -*- coding: utf-8 -*-
import unittest
import tempfile
from os.path import join, dirname, abspath
import os
from network_interfaces import InterfacesFile, Auto, Allow, ValidationError

__author__ = 'vahid'

this_dir = abspath(dirname(__file__))
data_dir = join(this_dir, 'data')

class NetworkingCase(unittest.TestCase):

    def setUp(self):
        self.interfaces_filename = join(data_dir, 'interfaces')

    def checkup_interfaces_file(self, filename):
        f = InterfacesFile(filename)

        self.assertRaises(KeyError, f.get_iface, 'non-existance-iface')

        lo = f.get_iface('lo')
        self.assertEquals(lo.startup.mode, 'auto')
        self.assertIsInstance(lo.startup, Auto)
        self.assertEquals(lo.name, 'lo')
        self.assertEquals(lo.address_family, 'inet')
        self.assertEquals(lo.method, 'loopback')

        eth0 = f.get_iface('eth0')
        self.assertEquals(eth0.startup.mode, 'auto')
        self.assertIsInstance(eth0.startup, Auto)
        self.assertEquals(eth0.name, 'eth0')
        self.assertEquals(eth0.address_family, 'inet')
        self.assertEquals(eth0.method, 'static')
        self.assertEquals(eth0.netmask, '255.255.255.240')
        self.assertEquals(eth0.broadcast, '192.168.11.15')
        self.assertEquals(eth0.network, '192.168.11.0')
        self.assertEquals(eth0.gateway, '192.168.11.1')
        self.assertEquals(eth0.dns_nameservers, '8.8.8.8 8.8.4.4')

        self.assertTrue(hasattr(eth0, 'netmask'))
        self.assertTrue('netmask' in eth0)
        self.assertFalse('lorem' in eth0)

        eth1 = f.get_iface('eth1')
        self.assertEquals(eth1.startup.mode, 'auto')
        self.assertIsInstance(eth1.startup, Auto)
        self.assertEquals(eth1.name, 'eth1')
        self.assertEquals(eth1.address_family, 'inet')
        self.assertEquals(eth1.method, 'dhcp')
        self.assertRaises(AttributeError, lambda: eth1.address)

        wlan0 = f.get_iface('wlan0')
        self.assertEquals(wlan0.startup.mode, 'allow-hotplug')
        self.assertIsInstance(wlan0.startup, Allow)
        self.assertEquals(wlan0.name, 'wlan0')
        self.assertEquals(wlan0.address_family, 'inet')
        self.assertEquals(wlan0.method, 'static')
        self.assertEquals(wlan0.address, '192.168.9.41')
        self.assertEquals(wlan0.netmask, '255.255.255.0')
        self.assertEquals(wlan0.broadcast, '192.168.9.255')
        self.assertEquals(wlan0.network, '192.168.9.0')
        self.assertEquals(wlan0.gateway, '192.168.9.1')
        self.assertEquals(wlan0.wpa_ssid, 'khayyam')
        self.assertEquals(wlan0.wpa_psk, '<-Wine&Is&Mine->')

        wlan1 = f.get_iface('wlan1')
        self.assertEquals(wlan1.startup.mode, 'auto')
        self.assertIsInstance(wlan1.startup, Auto)
        self.assertEquals(wlan1.name, 'wlan1')
        self.assertEquals(wlan1.address_family, 'inet')
        self.assertEquals(wlan1.method, 'dhcp')
        self.assertEquals(wlan1.wpa_ssid, 'Dorfak')
        self.assertEquals(wlan1.wpa_psk, 'ShoorPalangGoolakhTappeh')
        self.assertRaises(AttributeError, lambda: wlan1.address)

        eth2 = f.get_iface('eth2')
        self.assertEquals(eth2.startup.mode, 'auto')
        self.assertIsInstance(eth2.startup, Auto)
        self.assertEquals(eth2.name, 'eth2')
        self.assertEquals(eth2.script, '/usr/local/sbin/map-scheme')
        self.assertEquals(eth2.map_HOME, 'eth2-home')
        self.assertEquals(eth2.map_WORK, 'eth2-work')
        self.assertEquals(eth2.mappings, [
            ['map', 'HOME', 'eth2-home'],
            ['map', 'WORK', 'eth2-work']])

        eth2_home = f.get_iface('eth2-home')
        self.assertIsNone(eth2_home.startup)
        self.assertEquals(eth2_home.name, 'eth2-home')
        self.assertEquals(eth2_home.address_family, 'inet')
        self.assertEquals(eth2_home.method, 'static')
        self.assertEquals(eth2_home.address, '192.168.1.1')
        self.assertEquals(eth2_home.netmask, '255.255.255.0')
        self.assertEquals(eth2_home.up, 'flush-mail')

        return f

    def test_load_save(self):
        f1 = self.checkup_interfaces_file(self.interfaces_filename)
        h1 = hash(f1)
        f1.save(recursive=True)
        f2 = self.checkup_interfaces_file(self.interfaces_filename)
        h2 = hash(f2)
        self.assertEqual(h1, h2)

    def test_manipulation(self):
        temp_dir = tempfile.mkdtemp()
        os.mkdir(join(temp_dir, 'interfaces.d'))

        f1 = InterfacesFile(self.interfaces_filename)
        new_filename = join(temp_dir, 'interfaces')
        h1 = hash(f1)
        f1.save(recursive=True, filename=new_filename)
        f2 = self.checkup_interfaces_file(new_filename)
        h2 = hash(f2)
        self.assertEqual(h1, h2)

        eth0 = f2.get_iface('eth0')

        eth0.address = '192.168.11.2'
        self.assertEqual(eth0.address, '192.168.11.2')

        eth0.script = '/etc/network/if-up.d/eth0-up'
        self.assertEqual(eth0.script, '/etc/network/if-up.d/eth0-up')

        del eth0.netmask
        f2.save(new_filename, validate=False)

        f3 = InterfacesFile(new_filename)
        eth0 = f3.get_iface('eth0')
        self.assertEqual(eth0.address, '192.168.11.2')
        self.assertEqual(eth0.script, '/etc/network/if-up.d/eth0-up')
        self.assertRaises(AttributeError, lambda: self.netmask)
        #print eth0.netmask

    def test_validate(self):
        f1 = InterfacesFile(self.interfaces_filename)
        eth0 = f1.get_iface('eth0')
        self.assertTrue(eth0.validate())

        del eth0.network
        self.assertRaises(ValidationError, eth0.validate)
        self.assertTrue(eth0.validate(allow_correction=True))

        # del eth0.netmask
        # self.assertRaises(ValidationError, eth0.validate)
        # self.assertTrue(eth0.validate(allow_correction=True))

        eth0.address = '192.168.90.3'
        self.assertRaises(ValidationError, eth0.validate)





if __name__ == '__main__':
    unittest.main()

