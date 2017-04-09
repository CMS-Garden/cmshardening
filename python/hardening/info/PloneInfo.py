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
import sys
from hardening.info import InfoHandler
from hardening import io
from hardening.core import singleton


@singleton
@InfoHandler("plone")
# pylint: disable=too-few-public-methods
class PloneInfo(object):
    """
    provides information about the currently installed Plone CMS
    """

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.__plone_buildout = None

    def get_buildout(self):
        """
        Ask user for the location of the plone buildout directory
        """
        while self.__plone_buildout is None:
            self.__plone_buildout = io.create_writer().prompt_user_input(message=_(
                "Please specify the full path to your plone buildout directory. "
                "This directory is by default located in /opt/plone/ and contains the plone "
                "buildout.cfg. E.g.: /opt/plone/buildout/"))
            if (os.path.isdir(self.__plone_buildout) and
                    os.path.isdir(os.path.join(self.__plone_buildout, "var"))):
                return "dir:" + self.__plone_buildout
            else:
                self.__plone_buildout = None
                if not io.create_writer().prompt_user_yesno(message=_(
                        "The specified directory does not exists or is not the plone buildout "
                        "directory. Do you want to specify the path to your plone buildout "
                        "direcctory again? If your press \"no\" the script will abort.")):
                    sys.exit(0)
        return "dir:" + self.__plone_buildout
