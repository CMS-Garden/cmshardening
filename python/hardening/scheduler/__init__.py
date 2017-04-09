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

import importlib
import inspect
import os
import sys
import traceback
import logging
import six

import hardening.info as info
import hardening.storage as storage
from hardening import core
from hardening.utils.DisabledUtil import DisabledUtil
from hardening.utils.DisabledSection import DisabledSection
from hardening.utils.module.LeaveModule import LeaveModule
from hardening.utils.module.EnterModule import EnterModule, constants, io


# noinspection PyPep8Naming
class Scheduler(object):
    """ The Scheduler is responsible to run the right utils in the correct order

    This class can only be configured using the global options in `config.yml` and the
    module-specific options in the module-specific configuration files under the `modules`
    subdirectory.

    Scheduler will read the global RunUtils property and execute all modules whose name is stored in
    this list. If there is no corresponding YAML file in the `modules` subdirectory, then Scheduler
    will raise an error.

    If running in Interactive Mode, the user can select which modules shall run.
    """

    def __init__(self):
        # key:   name of package, e.g. 'ssh'
        # value: list which contains all modules in the package which should
        #        be invoked
        self.__modules = dict()
        self.__utils = []
        self.__module_state = self.__read_available_modules()

    def run_hardening_modules(self):
        """runs all configured modules

        This method calculates an execution order of core::HardeningUtil instances and runs the
        following methods, in order:

         -# core::HardeningUtil::run() is run for all utils
         -# core::HardeningUtil::finish() is run for all utils
         -# storage::TransactionManager::commit_all() is run

        If an error occurs or if the user interrupts the execution, then
        storage::TransactionManager::rollback_all() is run
        """
        try:
            self.__load_modules()

            for module, is_enabled in six.iteritems(self.__module_state):
                if is_enabled:
                    self.__load_utils(module)

            for util in self.__utils:
                util.setup()
                assert util.transaction().is_transaction_running()

        except KeyboardInterrupt:
            core.LogManager().get_logger().warning(
                _("aborting execution upon user request"))
            sys.exit(-1)
        except SyntaxError as error:
            core.LogManager().get_logger().fatal("%s" % str(error))
            self.print_stackstrace()
            sys.exit(-1)

        try:
            for util in self.__utils:
                util.run()

            for util in self.__utils:
                util.finish()

            self.__store_changes()
        except SystemExit:
            storage.TransactionManager().rollback_all()
            raise
        except KeyboardInterrupt:
            storage.TransactionManager().rollback_all()
            core.LogManager().get_logger().warning(
                _("aborting execution upon user request"))
            sys.exit(-1)
        except OSError as error:
            core.LogManager().get_logger().fatal("%s: %s" %
                                                 (str(error.strerror), error.filename))
            self.print_stackstrace()
            sys.exit(-1)
        except SyntaxError as error:
            core.LogManager().get_logger().fatal("%s" % str(error))
            self.print_stackstrace()
            sys.exit(-1)

    @staticmethod
    def print_stackstrace():
        if core.LogManager().get_loglevel() == logging.DEBUG:
            _, _, current_traceback = sys.exc_info()
            for frame in current_traceback.format_tb(current_traceback):
                for line in frame.strip().split("\n"):
                    core.LogManager().get_logger().fatal(line)

    @staticmethod
    def __store_changes():
        try:
            storage.TransactionManager().commit_all()
            if not core.RuntimeOptions().pretend_mode():
                io.create_writer().display_message(
                    headline=_("Backup location"),
                    message=_("backups have been written to '%(backupdir)s'")
                    % {'backupdir': storage.TransactionInfo().get_backupdir()})

        except SystemExit:
            # do not roll back after commit has been started
            storage.TransactionManager().rollback_all()
            raise
        except Exception as error:
            core.LogManager().get_logger().error(_("encountered an error, rolling back"))
            if core.LogManager().get_loglevel() == logging.DEBUG:
                core.LogManager().get_logger().fatal(error)
                traceback.print_exc(file=sys.stdout)

            # noinspection PyBroadException
            # pylint: disable=bare-except
            try:
                # do not roll back after commit has been started
                storage.TransactionManager().rollback_all()
            except:
                pass

            raise

    def __load_utils(self, module):
        self.__load_module_configuration(module)  # load meta information

        module_metainfo = info.Configuration().get_property(
            module, constants.CONFIG_META, default=None)

        # load introductory util
        self.__utils.append(EnterModule(
            option_values={
                constants.OPTION_MODULEMETA: module_metainfo,
                constants.CONFIG_RUNTIME: {
                    constants.OPTION_MODULE: module,
                    constants.OPTION_SECTION: None}}))

        # run all section of the current module which are enabled
        # (run-if must return True)
        for section in info.Configuration().get_property(
                module, constants.CONFIG_RUNSECTIONS):
            if self.__is_section_enabled(module, section):
                self.__load_section_utils(module, section)
            else:
                self.__utils.append(DisabledSection(
                    option_values={
                        constants.CONFIG_RUNTIME: {
                            constants.OPTION_SECTION: section,
                            constants.OPTION_CAUSE: info.Configuration().get_property(
                                module, section, constants.CONFIG_OPTIONS, constants.CONFIG_RUNIF,
                                default=None, interpolate=False)}}))

        # load ending util
        self.__utils.append(LeaveModule(
            option_values={
                constants.CONFIG_RUNTIME: {
                    constants.OPTION_MODULE: module
                }}))

    @staticmethod
    def __load_module_configuration(module):
        filename = os.path.join(
            core.RuntimeOptions().lib_path(), 'modules', module + '.yml')
        if os.path.exists(filename):
            # load configuration of the current module
            info.Configuration().merge_config_file(filename, module)

    def __load_modules(self):
        try:
            for module in info.Configuration().get_property(constants.CONFIG_RUNMODULES):
                if module not in self.__module_state.keys():
                    core.LogManager().get_logger().fatal(
                        "failure while trying to load module '%s'" % module)
                    sys.exit(-1)
                self.__module_state[module] = True
        except KeyboardInterrupt:
            core.LogManager().get_logger().warning(
                _("aborting execution upon user request"))
            sys.exit(-1)

        if not core.RuntimeOptions().silent_mode():
            self.__select_cms()
            self.__confirm_module_state()

    def __select_cms(self):
        cms_modules = info.Configuration().get_property(constants.CONFIG_CMSMODULES)
        selected_cms = io.create_writer().prompt_to_choose(
            message=_("Please select the CMS you wish to harden"),
            values=cms_modules + [_("none of them")]
        )

        # store information about which cms has been selected
        if selected_cms in cms_modules:
            core.RuntimeOptions().content_management_system = selected_cms
        else:
            core.RuntimeOptions().content_management_system = None

        # enable the corresponding module and disable all other cms modules
        for cms in cms_modules:
            if cms in self.__module_state:
                self.__module_state[cms] = (
                    cms == core.RuntimeOptions().content_management_system)

        # enable all default modules
        if core.RuntimeOptions().content_management_system:
            self.__load_module_configuration(
                core.RuntimeOptions().content_management_system)
            default_modules = info.Configuration().get_property(
                core.RuntimeOptions().content_management_system,
                constants.CONFIG_DEFAULTMODULES)
            for cms in default_modules:
                if cms in self.__module_state:
                    self.__module_state[cms] = True

    def __confirm_module_state(self):
        modules = sorted(set(self.__module_state.keys())
                         - set(info.Configuration().get_property(constants.CONFIG_CMSMODULES)))

        if core.RuntimeOptions().content_management_system:
            modules.insert(0, core.RuntimeOptions().content_management_system)

        while True:
            status_lines = list()
            idx = 1
            for module in modules:
                if self.__module_state[module]:
                    is_enabled = "*"
                else:
                    is_enabled = "-"
                status_lines.append("  [%s]  %2d: %s" %
                                    (is_enabled, idx, module))
                idx += 1

            io.create_writer().write_message(message="\n".join(status_lines),
                                             caption=_(
                                                 "Select modules to be run"),
                                             hint=_("number to toggle or Return to continue; "
                                                    "C to cancel"))
            result = io.create_writer().raw_input()
            if len(result) == 0:
                break
            if "cancel".startswith(result.lower()):
                sys.exit(0)

            try:
                idx = int(result) - 1
                if idx < 0 or idx >= len(modules):
                    raise ValueError()
                self.__module_state[modules[idx]
                                   ] = not self.__module_state[modules[idx]]
            except ValueError:
                pass

    def __load_section_utils(self, module, section):
        if not info.Configuration().has_property(
                module, section, constants.CONFIG_RUNUTILS):
            raise SyntaxError(
                _("missing %(runutils)s entry in module %(module)s and section %(section)s")
                % {"runutils": constants.CONFIG_RUNUTILS,
                   "module": module,
                   "section": section})

        for util_config in info.Configuration().get_property(module, section,
                                                             constants.CONFIG_RUNUTILS,
                                                             interpolate=False):
            util = self.__create_util_object(module, section, util_config)
            if util in self.__utils:
                core.LogManager().get_logger().info(_("util '%(util)s' is already scheduled")
                                                    % {'util': util})
            elif not util.is_enabled():
                core.LogManager().get_logger().info(_("util '%(util)s' is not enabled")
                                                    % {'util': util})
                self.__utils.append(DisabledUtil(
                    option_values={
                        constants.CONFIG_RUNTIME: {
                            constants.OPTION_UTIL: util,
                            constants.OPTION_CAUSE: util.get_option(constants.CONFIG_RUNIF, None,
                                                                    False)}}))
            else:
                self.__utils.append(util)

    @staticmethod
    def __is_section_enabled(module, section):
        res = info.Configuration().get_property(
            module, section, constants.CONFIG_OPTIONS, constants.CONFIG_RUNIF,
            default=True)
        if isinstance(res, bool):
            return res
        else:
            assert isinstance(res, list)
            return six.moves.reduce(lambda x, y: x and y, res)

    @staticmethod
    def __read_available_modules():
        modules = dict()
        searchpath = os.path.join(core.RuntimeOptions().lib_path(), 'modules')
        for _, _, files in os.walk(searchpath):
            for yaml_file in files:
                if yaml_file.endswith(".yml"):
                    modules[yaml_file.replace(".yml", "")] = False
        return modules

    def __create_util_object(self, module, section, util_cfg):
        (util_name, util_config), = list(util_cfg.items())
        section_options = info.Configuration().get_property(
            module, section, constants.CONFIG_OPTIONS, default=dict(), interpolate=False)

        # merge section options and util options:
        for opt in list(section_options.keys()):
            if opt not in list(util_config.keys()):
                util_config[opt] = section_options[opt]

        if constants.CONFIG_RUNTIME not in util_config.keys():
            util_config[constants.CONFIG_RUNTIME] = dict()
        util_config[constants.CONFIG_RUNTIME][constants.OPTION_MODULE] = module
        util_config[constants.CONFIG_RUNTIME][
            constants.OPTION_SECTION] = section

        pkg_name = 'hardening.utils' + '.' + util_name
        cls_name = util_name.split('.')[-1]

        pkg = importlib.import_module(pkg_name)
        cls = self.__import_class(pkg, cls_name)

        return cls(option_values=util_config)

    @staticmethod
    def __import_class(module, class_name):
        cls = getattr(module, class_name)

        # we could have used issubclass here, but we had to avoid importing
        # HardeningUtil
        if 'utils.HardeningUtil.HardeningUtil' not in [x.__module__ + "." + x.__name__ for x in
                                                       inspect.getmro(cls)]:
            core.LogManager().get_logger().debug(_("imported %(module)s.%(class)s") %
                                                 {'module': module.__name__,
                                                  'class': cls.__name__})
            return cls
        else:
            core.LogManager().get_logger().warn(class_name +
                                                _(" is not a subclass of HardeningUtil"))
            return None

    @staticmethod
    def __package_prefix(package):
        package_basepath = os.path.dirname(inspect.getfile(package))

        _, part = os.path.split(package_basepath)
        return part
