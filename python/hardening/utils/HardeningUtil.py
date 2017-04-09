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
from abc import ABCMeta, abstractmethod
from hardening import io, info, storage, core, constants
from hardening.info.lib.PackageManager import PackageManager

import six


class HardeningUtil(six.with_metaclass(ABCMeta)):
    """
    parent class for all hardening utils that write or read a configuration file or execute a
    command holding base functions for initializing needed values and storing metainformation as
    well as transactions
    """

    def __init__(self, **kwargs):
        if 'option_values' in kwargs:
            option_values = kwargs['option_values']
        else:
            option_values = dict()

        self.__transaction = None

        for opt in option_values.keys():
            if opt not in self.valid_options():
                if opt == constants.OPTION_TRANSACTION and self.required_transaction is not None:
                    continue
                if opt == constants.OPTION_MODULE or \
                        opt == constants.OPTION_SECTION or \
                        opt == constants.OPTION_UTIL:
                    continue
                raise SyntaxError("unknown option '%(option)s' for '%(class)s'"
                                  % {'option': opt, 'class': self.__class__.__name__})

        self.__option_values = option_values

        for opt in self.required_options():
            if opt not in option_values.keys():
                raise SyntaxError(
                    _("missing argument '%(option)s' for module %(class)s")
                    % {'option': opt, 'class': self.__class__.__name__})

        if self.required_transaction() is not None:
            configured_transaction = self.transaction()
            if not (configured_transaction.__class__ == self.required_transaction() or
                    issubclass(configured_transaction.__class__, self.required_transaction())):
                raise SyntaxError(
                    _("this module requires a transaction of type %(transaction)s")
                    % {'transaction': self.required_transaction()})

        missing_packages = list()
        for pkg in self.required_packages():
            if not PackageManager().get_package_manager().is_package_installed(pkg):
                missing_packages.append(pkg)

        if len(missing_packages) > 0:
            if len(missing_packages) == 1:
                message = _("the following package is required, "
                            "but not installed: '%(package)s'") % \
                    {'package': missing_packages[0]}
            else:
                message = _("the following packages are required, "
                            "but not installed: %(package)s") % \
                    {'package': ", ".join(
                        ["'" + x + "'" for x in missing_packages])}
            raise SyntaxError(message)

    @property
    def option_values(self):
        return self.__option_values

    def get_option(self, key, default_value=None, interpolate=True):
        if key not in self.valid_options():
            raise SyntaxError(
                "invalid option requested: '%(key)s' in '%(class)s'"
                % {'key': str(key), 'class': self.__class__.__name__})

        if key not in self.__option_values:
            return default_value

        raw_value = self.__option_values[key]
        if raw_value is None:
            result = io.create_writer().prompt_user_input(property_name=key)
        else:
            if interpolate:
                result = info.Configuration().interpolate(raw_value)
            else:
                result = raw_value

        return result

    def get_str_option(self, key, default_value=None):
        opt = self.get_option(key, default_value=default_value)
        if opt is None:
            return None
        if isinstance(opt, str):
            return opt
        raise ValueError(
            _("invalid datatype for key '%(key)s'" % {'key': key}))

    def has_option(self, key):
        return key in self.__option_values

    def is_enabled(self):
        res = self.get_option(constants.CONFIG_RUNIF, None)
        if res is None:
            return True
        if isinstance(res, bool):
            return res
        elif isinstance(res, str):
            return info.Configuration().interpolate(res)
        else:
            assert isinstance(res, list)
            return six.moves.reduce(lambda x, y: x and y,
                                    [info.Configuration().interpolate(r) for r in res])

    @staticmethod
    def store_result(*key, **kwargs):
        result = kwargs['result']
        assert isinstance(result, str) or isinstance(
            result, list) or isinstance(result, bool)
        info.Configuration().set_property(*key, value=result)

    def __eq__(self, other):
        res = self.__class__.__name__ == other.__class__.__name__ \
            and self.option_values == other.option_values
        return res

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__class__.__name__

    def get_transaction_key(self):
        if constants.CONFIG_TRANSACTION not in self.__option_values.keys():
            return None
        return info.Configuration().interpolate(
            self.__option_values[constants.CONFIG_TRANSACTION])

    @staticmethod
    def get_transaction_kwargs():
        return {}

    def transaction(self):
        return storage.TransactionManager().create_transaction(
            self.get_transaction_key(),
            **self.get_transaction_kwargs())

    def setup(self):
        self.transaction().begin()
        assert self.transaction().is_transaction_running()

        core.LogManager().get_logger().debug(
            _("running %(transaction)s.begin()"), {'transaction': self.transaction().url()})

        self.__invoke(self.__setup__)

    def __setup__(self):
        pass

    def finish(self):
        core.LogManager().get_logger().debug(
            _("running %(transaction)s.finish()"), {'transaction': self.__class__.__name__})

        self.__invoke(self.__finish__)

    def __finish__(self):
        pass

    @abstractmethod
    def __run__(self):
        pass

    def run(self):
        core.LogManager().get_logger().debug(
            _("running %(transaction)s.run()"), {'transaction': self.__class__.__name__})
        self.print_metainfo()
        self.__invoke(self.__run__)

    def print_metainfo(self):
        io.create_writer().display_message(
            headline=self.get_metainfo(constants.CONFIG_CAPTION),
            message=self.get_metainfo(constants.CONFIG_DESCRIPTION))

    def get_metainfo(self, opt):
        meta = self.get_option(constants.CONFIG_META)
        if meta is None:
            return None

        if isinstance(meta, dict):
            if opt in meta.keys():
                return meta[opt]
            else:
                return None

        assert isinstance(meta, list)

        # complete match (e.g. en_US)
        for localized_meta in [m for m in meta if isinstance(m, dict)]:
            language = core.RuntimeOptions().get_locale()
            if language == localized_meta[constants.CONFIG_LANGUAGE] and \
                    opt in localized_meta.keys():
                return localized_meta[opt]

        # language match (e.g. en)
        for localized_meta in [m for m in meta if isinstance(m, dict)]:
            language = core.RuntimeOptions().get_locale().split("_")[0]
            if language == localized_meta[constants.CONFIG_LANGUAGE] and \
                    opt in localized_meta.keys():
                return localized_meta[opt]

        return None

    def get_runtimeinfo(self, opt, interpolate=True):
        runtimeinfo = self.get_option(
            constants.CONFIG_RUNTIME, interpolate=interpolate)
        if runtimeinfo is None or opt not in runtimeinfo.keys():
            return None

        return runtimeinfo[opt]

    def get_caption(self):
        return self.get_metainfo(constants.CONFIG_CAPTION)

    def get_description(self):
        return self.get_metainfo(constants.CONFIG_DESCRIPTION)

    def __invoke(self, method):
        self.__set_current_util()
        method()
        self.__release_current_util()

    def __set_current_util(self):
        # module and util should be set always
        core.ExecutionState().current_module = self.get_runtimeinfo(constants.OPTION_MODULE)
        core.ExecutionState().current_section = self.get_runtimeinfo(constants.OPTION_SECTION)
        core.ExecutionState().current_util = self

    @staticmethod
    def __release_current_util():
        core.ExecutionState().current_module = None
        core.ExecutionState().current_section = None
        core.ExecutionState().current_util = None
