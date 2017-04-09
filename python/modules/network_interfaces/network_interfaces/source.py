# -*- coding: utf-8 -*-
from .stanza import Stanza
__author__ = 'vahid'

class Source(Stanza):
    _type = 'source'

    @property
    def source_filename(self):
        return self._headers[1]

    @source_filename.setter
    def source_filename(self, val):
        self._headers[1] = val


class SourceDirectory(Stanza):
    _type = 'source-directory'

    @property
    def source_directory(self):
        return self._headers[1]

    @source_directory.setter
    def source_directory(self, val):
        self._headers[1] = val
