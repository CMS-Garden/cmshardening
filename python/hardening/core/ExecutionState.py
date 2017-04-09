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

from hardening.core.Singleton import singleton


@singleton
class ExecutionState(object):
    """
    represents meta information about the current state of execution, i.e. which module
     is currenty running.
    """

    def __init__(self):
        self.__current_module = None
        self.__current_section = None
        self.__current_util = None

    @property
    def current_module(self):
        return self.__current_module

    @current_module.setter
    def current_module(self, module):
        self.__current_module = module

    @property
    def current_section(self):
        return self.__current_section

    @current_section.setter
    def current_section(self, section):
        self.__current_section = section

    @property
    def current_util(self):
        return self.__current_util

    @current_util.setter
    def current_util(self, util):
        self.__current_util = util
