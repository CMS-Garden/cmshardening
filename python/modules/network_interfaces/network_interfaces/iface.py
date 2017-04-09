# -*- coding: utf-8 -*-
from .stanza import MultilineStanza
from .errors import ValidationError
__author__ = 'vahid'


class IfaceBase(MultilineStanza):
    startup = None

    @property
    def name(self):
        return self._headers[1]

    @name.setter
    def name(self, val):
        self._headers[1] = val

    def __hash__(self):
        return hash(self.startup) ^ super(IfaceBase, self).__hash__()

    def __repr__(self):
        if self.startup:
            return '%s\n%s' % (self.startup, super(IfaceBase, self).__repr__())
        return super(IfaceBase, self).__repr__()


class Iface(IfaceBase):
    _type = 'iface'

    @property
    def address_family(self):
        return self._headers[2]

    @address_family.setter
    def address_family(self, val):
        self._headers[2] = val

    @property
    def method(self):
        return self._headers[3]

    @method.setter
    def method(self, val):
        self._headers[3] = val

    @property
    def address_netmask(self):
        return '%s/%s' % (self.address, self.netmask)

    def validate(self, allow_correction=False):
        return True


class Mapping(IfaceBase):
    _type = 'mapping'

    def __getattr__(self, item):
        if item.startswith('map_'):
            map_name = item.split('_')[1]
            key = map_name.replace('_', '-')
            return ' '.join([i for i in self._items if i[0] == 'map' and i[1] == key][0][2:])
        return super(Mapping, self).__getattr__(item)

    @property
    def mappings(self):
        return [i for i in self._items if i[0] == 'map']
