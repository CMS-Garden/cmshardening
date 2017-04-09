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

import inspect
import os
import re
import sys

from hardening import info
from hardening.info.lib import OSInfo


@info.InfoHandler("resolve_key")
# pylint: disable=too-few-public-methods
class ResolveKey(object):
    """
    this class can be used to perform simple text replacements, based on OSInfo::distribution_name()

    See ResolveKey::interpolate() for details.
    """

    def __init__(self):
        package_basepath = os.path.dirname(
            inspect.getfile(sys.modules[self.__class__.__module__]))
        info.Configuration().merge_config_file(
            os.path.join(package_basepath, "config.yml"), "info")

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def interpolate(self, keyname):
        """Uses entries in `config.yml` to interpolate.

        Each `keyname` is mapped to an associative list, where the key is a regular expression that
        is matched against the result of OSInfo::distribution_name(). If the distribution name
        matches the given regular expression, then the interpolated string is replaced by the value
        of the associative list from `config.yml`
        """
        prop = info.Configuration().get_property("info", keyname)
        if prop is None:
            raise SyntaxError(
                _("invalid info key in configuration: '%(keyname)s'")
                % {'keyname': keyname})

        for _os in list(prop.keys()):
            if re.match(_os, OSInfo().distribution_name()):
                return prop[_os]

        raise SyntaxError(_("found no value for info key '%(keyname)s'")
                          % {'keyname': keyname})
