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
import re
import yaml
from hardening import core, io, constants


@core.singleton
class Info(object):
    """
    Info is the entry point to the different info modules, which handle properties that start
    with `info:...`
    """

    def __init__(self):
        self.__handlers = dict()
        libpath = os.path.dirname(
            inspect.getfile(sys.modules[self.__class__.__module__]))

        for filepath in os.listdir(libpath):
            if filepath.endswith('.py'):
                filename = os.path.basename(filepath)
                if filename.startswith("__"):
                    continue

                importlib.import_module(
                    self.__module__ + "." + filename.replace(".py", ""))

    def register_info_handler(self, schema, handler):
        self.__handlers[schema] = handler

    def interpolate(self, value):
        value_parts = value.split(":")

        if value_parts[0] not in self.__handlers:
            raise SyntaxError(
                _("found no value for info key '%(key)s'") % {'key': value})

        handler = self.__handlers[value_parts[0]]

        # handle object methods
        for name, method in inspect.getmembers(handler, inspect.ismethod):
            if name == "get_%s" % value_parts[1]:
                return method(*value_parts[2:])

        # handle static methods
        for name, method in inspect.getmembers(handler, inspect.isfunction):
            if name == "get_%s" % value_parts[1]:
                return method(*value_parts[2:])

        core.LogManager().get_logger().info(
            _("using default interpolate method for value '%(key)s'") % {'key': value})
        try:
            return self.__handlers[value_parts[
                0]].interpolate(*value_parts[1:])
        except AttributeError:
            raise AttributeError(
                _("missing handler for '%(key)s'") % {'key': value})


# pylint: disable=too-few-public-methods
class InfoHandler(object):
    """
    Decorator for classes which are are responsible to handle info properties.

    A class which will be responsible for `info:example:property` will instantiate this decorator
    as follows:

        @InfoHandler('example')
        class ExampleInfo:
            def get_property(*_):
                pass
    """

    def __init__(self, infoschema):
        super(InfoHandler, self).__init__()
        self.__infoschema = infoschema

    def __call__(self, cls):
        Info().register_info_handler(self.__infoschema, cls())
        cls.keyword = staticmethod(lambda: self.__infoschema)
        return cls


@core.singleton
class Configuration(object):
    """provides access to the configuration repository.

    Properties are read from YAML-formated configuration files `config.yml` and `modules/*.yml` and
    can be accessed using the method Configuration::get_property.

    This class is a Singleton and should be used as such; do not store references to a Configuration
    object
    """

    def __init__(self):
        self.__properties = {}
        self.__properties_yaml = {}

        config_file = os.path.join(core.RuntimeOptions().base_path(),
                                   constants.FILENAME_LOCALCONFIG)

        with open(config_file, 'r') as stream:
            stream_content = stream.read(-1)
            self.set_config(stream_content)

    def get_property(self, *name_parts, **kwargs):
        """retrieve information from the configuration repository

        You can imagine the configuration repository as a tree, where each node has a name
        (similar to filesystem objects such as files and directories). Properties are identified
        using a list of property names, where the first entry identifies the child of the root
        node whose name is equal to the first list entry, the second entry identifies the child
        of the latter node whose name is equal to the second list entry and so on.

        The last list entry identifies the property itself.

        For example, consider the following configuration repository:

                                +-----+
                         +------+     +------+
                         |      +-----+      |
                         |         |         |
                         |         |         |
                      +--+--+   +--+--+   +--+--+
               +------+  A  |   |  B  |   |  C  |
               |      +-----+   +-----+   +-----+
               |         |  +------+
               |         |         |
            +--+--+   +-----+   +--+--+
            |  x  |   |  y  |   |  z  |
            +-----+   +-----+   ++-+-++
                                 | | |
                         +-------+ | +-------+
                      +--+--+   +--+--+   +--+--+
                      |  a  |   |  b  |   |  c  |
                      +-----+   +-----+   +-----+


        In this example, the following property names are valid and have a value:

        | Property name     |
        | ----------------- |
        | `` ['A', 'x'] ``    |
        | `` ['A', 'y'] ``    |
        | `` ['A', 'z', 'a'] `` |
        | `` ['A', 'z', 'b'] `` |
        | `` ['A', 'z', 'c'] `` |
        | `` ['B'] `` |
        | `` ['C'] `` |

        @param name_parts: contains the list of names which identify the property to be retrieved.
        If this list does not contain the full path of the property, but only a part,
        then a subtree of the configuration repository will be returned

        @param kwargs:
         * if kwargs contains `default` and no property with the specified name is not found the
           repository, then the value of the `default` key will be returned.
         * if kwargs contains `interpolate` and its value is `True`,
           then Configuration::interpolate will be called on the return value

        @return
         * If the specified property is found, then its value will be returned.
         * If the name specifies a subtree of the repository, then the subtree will be returned
         * if the property is not found, but a default value has been specified, then this will be
           returned
         * None otherwise
        """
        value = self.__get_property(*name_parts)
        if value is None:
            if 'default' not in list(kwargs.keys()):
                return self.__prompt_user_property(*name_parts)
            else:
                return kwargs['default']
        elif 'interpolate' in list(kwargs.keys()) and not kwargs['interpolate']:
            return value
        else:
            return self.interpolate(value)

    def has_property(self, *name_parts):
        """determines if a property is available in the repository

        @param name_parts: name of the property. For details about property naming have a look at
            Configuration::get_property
        @return `True` if the property exists, `False` otherwise
        """
        value = self.__get_property(*name_parts)
        return value is not None

    def interpolate(self, value):
        """traverses the given datastructure recursively and calls Configuration::interpolate_atom
        on every atomic item

        @param value: the datastructure to be interpolated
        @return the same datastructure as provided as an argument,
        but all atomic values (i.e. strings) in it have been replaced by the result of the call to
        Configuration::interpolate_atom
        """
        if isinstance(value, list):
            return [self.interpolate(v) for v in value]
        elif isinstance(value, dict):
            return {k: self.interpolate(v) for k, v in list(value.items())}
        else:
            return self.interpolate_atom(value)

    @staticmethod
    def interpolate_atom(value):
        """ if `value` is a string this method replaces special sub strings, according to the
        following rules:

        1. if the substring starts with `info:`, the remaining substring will be passed to
           Info::interpolate
        2. if the substrings starts with `$`, it is assumed to be an environment variable and will
           replaced by the
           value of that variable if it exists

        @param value: string, to be interpolated
        @return interpolated string
        """
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        info_regex = r".*?{(info:[\-\:\.\_0-9a-zA-Z]*)}"
        matches = re.findall(info_regex, value)

        if matches:
            for match in matches:
                tmpmatch = ":".join(match.split(":")[1:])
                tmpvalue = Info().interpolate(tmpmatch)
                if match == value:
                    value = tmpvalue
                else:
                    assert isinstance(match, str)
                    assert isinstance(tmpvalue, str)
                    value = value.replace("{" + match + "}", tmpvalue)

        info_regex = r".*?(info:[\-\:\.\_0-9a-zA-Z]*)"
        matches = re.findall(info_regex, value)

        if matches:
            for match in matches:
                if match != value:
                    core.LogManager().get_logger().info("using obsolete info-format: '%(match)s'"
                                                        % {'match': match})
                tmpmatch = ":".join(match.split(":")[1:])
                tmpvalue = Info().interpolate(tmpmatch)
                if match == value:
                    value = tmpvalue
                else:
                    value = value.replace(match, tmpvalue)
        return value

    def set_property(self, *name_parts, **kwargs):
        """adds some property to the repository if it does not exit, or overwrites the existing
        value

        @param name_parts: name of the property. For details about property naming have a look at
            Configuration::get_property
        @param kwargs: if `kwargs` contains the key 'value', then its value will be used to set
        the property; otherwise `None` will be used
        """
        if 'value' not in kwargs.keys():
            kwargs['value'] = None

        ptr = self.__properties
        for part in name_parts[:-1]:
            if part not in ptr.keys():
                ptr[part] = dict()

            ptr = ptr[part]

        ptr[name_parts[-1]] = kwargs['value']

    def set_config(self, cfg_string):
        """ sets (or overwrites) the configuration repository

        @param cfg_string: YAML-formated string which contains the new configuration
        """
        self.__properties_yaml[''] = cfg_string
        self.__properties = yaml.load(cfg_string)

    def merge_config_file(self, filename, prefix):
        """ adds the contents of a YAML file to the configuration repository

        The contents of the YAML file will be added to the root level of the repository, because
        this could overwrite existing values in case of name clashes. Instead you have to provide
        a prefix, which will be used as first property name part (see Configuration::get_property).
        For example, if you load a property named 'MyProperty' from a YAML file using the prefix
        `MyPrefix`, then this property can later be read by the identifier
        ``['MyPrefix', 'MyProperty']``.

        @param filename: name of the YAML file
        @param prefix: prefix to be used. If properties with the same prefix exist already, then
        the whole subtree with this prefix will be overwritten!
        """
        if not os.path.exists(filename):
            return

        with open(filename, 'rb') as stream:
            try:
                if sys.hexversion >= 0x03000000:
                    yaml_stream = os.linesep.join(
                        ["    " +
                         x for x in stream.read(-1).decode('utf-8').split("\n")]
                    )
                else:
                    yaml_stream = os.linesep.join(
                        ["    " + x for x in stream.read(-1).split("\n")]
                    )
            except UnicodeDecodeError:
                core.LogManager().get_logger().fatal(
                    _("invalid file encoding in file '%(filename)s'")
                    % {'filename': filename})
                sys.exit(-1)

            if prefix not in self.__properties_yaml:
                self.__properties_yaml[prefix] = prefix + ":" + os.linesep

            # append the contents of the new config file
            # to the current config string
            self.__properties_yaml[prefix] += os.linesep + yaml_stream

            try:
                # reparse the whole config string to force the yaml parser
                # to evaluate 'repeated nodes'
                config = yaml.load("\n".join(self.__properties_yaml.values()))
                if config is not None:
                    self.__properties = config
            except yaml.YAMLError:
                stream.seek(0)
                error = None
                try:
                    yaml.load(stream.read().decode('utf-8'))
                except yaml.YAMLError as yaml_error:
                    error = yaml_error
                assert error is not None

                core.LogManager().get_logger().error(_("error while parsing '%(filename)s'")
                                                     % {'filename': filename})
                core.LogManager().get_logger().error(str(error))
                sys.exit(-1)

    def __get_property(self, *name_parts):
        ptr = self.__properties
        for part in name_parts:
            if part not in list(ptr.keys()):
                return None

            ptr = ptr[part]
            if ptr is None:
                return None
        return ptr

    @staticmethod
    def __prompt_user_property(property_type=str, *name_parts):
        if property_type == bool:
            return io.create_writer().prompt_user_yesno(property_name='.'.join(name_parts))
        else:
            return io.create_writer().prompt_user_input(property_name='.'.join(name_parts))
