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

from hardening import constants
from hardening.utils.HardeningUtil import HardeningUtil


class UtilOption(object):
    """
    valid options for the hardening utils
    """

    def __init__(self, name, required=False, docstring=None):
        self.__name = name
        self.__required = required
        self.__docstring = docstring

    def get_name(self):
        return self.__name

    def get_docstring(self):
        return self.__docstring

    def is_required(self):
        return self.__required

    def __str__(self):
        return "UtilOption: " + self.__name


#pylint: disable=too-few-public-methods
class ModuleSettings(object):
    """
    decorator class for the hardening utils
    """

    def __init__(self,
                 options=None,
                 required_transaction=None,
                 required_packages=None):
        if required_packages is None:
            required_packages = []
        if options is None:
            options = []
        self.__transaction = required_transaction
        self.__required_packages = required_packages

        self.__required_options = set()
        self.__valid_options = set()

        # adding predefined values:
        self.__add_valid_option(options, constants.CONFIG_META,
                                _("contains information about that specific hardening step"))
        self.__add_valid_option(options, constants.CONFIG_RUNTIME,
                                _("contains runtime information about this hardening step"))
        self.__add_valid_option(options, constants.CONFIG_RUNIF,
                                _("specifies under which condition this util will be run"))

        self.__options = options

        for opt in options:
            if not isinstance(opt, UtilOption):
                raise SyntaxError("invalid entry in options list: " + str(opt))

            if opt.is_required():
                self.__required_options.add(opt.get_name())
            self.__valid_options.add(opt.get_name())

    @staticmethod
    def __add_valid_option(options, option_id, option_doc):
        if option_id not in options:
            options.append(UtilOption(
                option_id, required=False, docstring=option_doc))

    def __call__(self, cls):
        cls.valid_options = staticmethod(lambda: self.__valid_options)
        cls.required_options = staticmethod(lambda: self.__required_options)
        cls.required_transaction = staticmethod(lambda: self.__transaction)
        cls.required_packages = staticmethod(lambda: self.__required_packages)

        if not self.__required_options.issubset(self.__valid_options):
            diff = self.__required_options.difference(self.__valid_options)
            raise SyntaxError("invalid options in class %(class)s: %(diff)s"
                              % {'class': cls.__name__, 'diff': str(diff)})

        cls.options = staticmethod(lambda: self.__options)

        return cls
