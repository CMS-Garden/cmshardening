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

from hardening import info


@info.InfoHandler("property")
# pylint: disable=too-few-public-methods
class Property(object):
    """
    This class can be used to query properties from any yaml file. Internally, this class calls
    Configuration::get_property()
    """

    @staticmethod
    def get_get(keyname):
        property_key = keyname.split(".")
        if len(property_key) <= 0:
            raise RuntimeError(
                "invalid property name requested: '%s'" % keyname)
        return info.Configuration().get_property(*property_key)
