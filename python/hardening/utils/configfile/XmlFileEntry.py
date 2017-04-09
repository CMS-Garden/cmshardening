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


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_TRANSACTION,
                         required=True,
                         docstring="path of the config file"),
        utils.UtilOption(constants.OPTION_XSLT,
                         required=True,
                         docstring="XML transform to be applied to the configuration file"),
        utils.UtilOption(constants.OPTION_XMLNS,
                         required=False,
                         docstring="default XML namespace used in the file"),
        utils.UtilOption(constants.OPTION_XMLNSPREFIX,
                         required=False,
                         docstring="XML namespace prefix used in the file")
    ],
    required_transaction=storage.XmlTransaction)
class XmlFileEntry(utils.HardeningUtil):
    """
    specialized util allowing the modification of xml files with xslt standard
    """

    def __init__(self, **kwargs):
        super(XmlFileEntry, self).__init__(**kwargs)
        self.__xslt = None

    def __setup__(self):
        if self.get_option(constants.OPTION_XMLNS) is not None \
                and self.get_option(constants.OPTION_XMLNSPREFIX) is not None:
            namespace_definition = \
                ' xmlns:%s="%s" exclude-result-prefixes="%s" ' % \
                (self.get_option(constants.OPTION_XMLNSPREFIX),
                 self.get_option(constants.OPTION_XMLNS),
                 self.get_option(constants.OPTION_XMLNSPREFIX))
        else:
            namespace_definition = ""

        self.__xslt = "\n".join([
            '''<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform" %s>'''
            % namespace_definition,
            ' <xsl:output omit-xml-declaration="no" indent="yes" '
            'method="xml"/>',
            ''' <xsl:variable name="%s" select="'%s'" />''' % (
                constants.OPTION_XMLNS,
                self.get_option(constants.OPTION_XMLNS)),
            self.get_option(constants.OPTION_XSLT),
            '''
            <xsl:template match="*|/|comment()|processing-instruction()"
            priority="-1">
                <xsl:copy>
                    <xsl:copy-of select="@*" />
                    <xsl:apply-templates />
                </xsl:copy>
            </xsl:template>
            </xsl:stylesheet>
            '''
        ])

    def __run__(self):
        self.transaction().transform(self.__xslt)
