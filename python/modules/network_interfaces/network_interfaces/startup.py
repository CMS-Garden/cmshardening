# -*- coding: utf-8 -*-
from .stanza import Stanza
__author__ = 'vahid'

class StartupStanza(Stanza):
    @property
    def mode(self):
        return self._headers[0]

    @property
    def iface_name(self):
        return self._headers[1]


class Auto(StartupStanza):
    _type = 'auto'


class Allow(StartupStanza):
    _type = 'allow-'

