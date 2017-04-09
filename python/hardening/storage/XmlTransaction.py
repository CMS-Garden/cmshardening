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

import os
import difflib
from lxml import etree, objectify
from hardening import core, io
from hardening.storage import StorageHandler
from hardening.storage.FileTransaction import FileTransaction


@StorageHandler("xml")
class XmlTransaction(FileTransaction):
    """
    Transaction class for xml files allowing modifications and storing of changes for this file type
    """

    def __init__(self, filename):
        super(XmlTransaction, self).__init__(filename)
        self.__xml = None
        self.__original_xml = None

    def __begin__(self):
        FileTransaction.__begin__(self)
        self.__original_xml = objectify.fromstring(self.read())
        self.__xml = self.__original_xml

    def must_apply_changes(self):
        if core.RuntimeOptions().pretend_mode():
            apply_changes = False
        else:
            apply_changes = True

        if core.RuntimeOptions().difference_mode() and self.has_modifications_to_save():
            diff = list(
                difflib.unified_diff(self.__prettyprint(self.__original_xml).split(os.linesep),
                                     self.__prettyprint(
                                         self.__xml).split(os.linesep),
                                     fromfile=self.url()))

            # be aware: we cannot use self.prompt_user here, because this method expects a
            # HardeningUtil-instance somewhere on the stack. But must_apply_changes is called
            # during Transaction.commit(); i.e. afterall HardeningUtils have
            # been run
            if len(diff) > 0 and not io.create_writer().prompt_user_yesnocancel(
                    _("Do you want to apply the following changes to '%(filename)s'")
                    % {'filename': self.url()}, quoted=diff):
                apply_changes = False
        elif core.RuntimeOptions().interactive_mode():
            apply_changes = self.has_modifications_to_save()
        return apply_changes

    def transform(self, xslt):
        xslt_root = etree.XML(xslt)
        trx = etree.XSLT(xslt_root)

        before = self.__prettyprint(self.__xml).split(os.linesep)
        transformed = trx(self.__xml)
        after = self.__prettyprint(transformed).split(os.linesep)

        if core.RuntimeOptions().interactive_mode() and after != before:
            diff = list(difflib.unified_diff(before, after))
            if len(diff) > 0 and not self.prompt_user(
                    _("Do you want to apply the following changes to '%(filename)s'")
                    % {'filename': self.url()}, quoted=diff):
                return

        if after != before:
            self.__xml = transformed
            self.mark_as_modified()

    @staticmethod
    def __prettyprint(xml):
        """ inspired by
        http://blog.humaneguitarist.org/2011/11/12/pretty-printing-xml-with-python-lxml-and-xslt/

        for more on lxml/XSLT see: http://lxml.de/xpathxslt.html#xslt-result-objects
        """
        xslt_tree = etree.XML('''
                <!-- XSLT taken from Comment 4 by Michael Kay found here:
                http://www.dpawson.co.uk/xsl/sect2/pretty.html#d8621e19 -->
                <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
                <xsl:strip-space elements="*"/>
                <xsl:template match="/">
                <xsl:copy-of select="."/>
                </xsl:template>
                </xsl:stylesheet>''')
        transform = etree.XSLT(xslt_tree)
        result = transform(xml)
        # noinspection PyUnresolvedReferences
        return unicode(result)

    def new_file_content(self):
        return self.__prettyprint(self.__xml)

    def log_changes(self):
        diff = list(difflib.unified_diff(self.__prettyprint(self.__original_xml).split(os.linesep),
                                         self.__prettyprint(
                                             self.__xml).split(os.linesep),
                                         fromfile=self.url()))
        if len(diff) > 0:
            core.ChangeLog().append_log_item("###########################################")
            core.ChangeLog().append_log_item("patch '%s' <<EOF" % self.url())
            core.ChangeLog().append_log_item(*diff)
            core.ChangeLog().append_log_item("EOF")


# pylint: disable=no-member
FileTransaction.register(XmlTransaction)
