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

"""
initialising the internationalization with the specified locale
"""

import gettext
import inspect
import os
import sys
# noinspection PyPep8
from hardening.core import RuntimeOptions

__version__ = '0.9'
__programname__ = 'hardening.py'

LOCALE_DIR = os.path.abspath(os.path.join(os.path.dirname(
    inspect.getfile(inspect.currentframe())), os.pardir, "locale"))


def install_default_translation():
    try:
        current_translation = gettext.translation(domain="hardening_messages",
                                                  localedir=LOCALE_DIR)
    except IOError:
        current_translation = gettext.translation(domain="hardening_messages",
                                                  languages=['en_US'],
                                                  localedir=LOCALE_DIR)
    __install_translation(current_translation)

def install_user_translation():
    current_translation = gettext.translation(domain="hardening_messages",
                                              languages=[
                                                  RuntimeOptions().get_locale()],
                                              localedir=LOCALE_DIR)
    __install_translation(current_translation)

def __install_translation(current_translation):
    if sys.version_info > (3, 0):
        current_translation.install()
    else:
        current_translation.install(unicode=True)

install_default_translation()

if RuntimeOptions().get_locale() is not None:
    install_user_translation()
