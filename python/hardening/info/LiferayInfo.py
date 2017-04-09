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
from hardening.core import singleton
from hardening import io
from hardening.info import InfoHandler


@singleton
@InfoHandler("liferay")
# pylint: disable=too-few-public-methods
class LiferayInfo(object):
    """
    provides information about the currently installed Liferay CMS
    """

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.__liferay_home = "/opt/liferay/liferay-home"

    def get_home(self):
        if os.path.exists(self.__liferay_home):
            return self.__liferay_home

        self.__liferay_home = io.create_writer().prompt_user_input(
            _("Please type the path of your liferay home directory"),
            default=self.__liferay_home,
            validator=os.path.isdir)

        return self.__liferay_home
