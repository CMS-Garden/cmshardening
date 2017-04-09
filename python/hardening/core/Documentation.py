import importlib
import inspect
import os
import re

from hardening.core.RuntimeOptions import RuntimeOptions
from hardening.core.Singleton import singleton


@singleton
class Documentation(object):
    """
    generates markdown-formatted documentation for utils and info classes
    """

    @staticmethod
    def __get_generic_documentation():
        template_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
        template_file = os.path.join(template_dir, "README_template.md")
        with open(template_file) as code_file:
            return code_file.read()

    @staticmethod
    def __create_util_documentation():
        base_path = RuntimeOptions().base_path()
        searchpath = os.path.join(base_path, 'hardening', 'utils')
        result = [
            '|util class| option |is required?|meaning',
            '|-|-|-|-'
        ]

        for root, _, files in os.walk(searchpath):
            for code_file in files:
                if code_file.endswith(".py"):
                    module_name = os.path.join(root.replace(base_path + os.sep, ""),
                                               code_file[:-3]).replace('/', '.')
                    class_name = module_name.split(b'.')[-1].decode()

                    pkg = importlib.import_module(module_name)

                    cls = getattr(pkg, class_name)

                    if not inspect.isclass(cls):
                        continue

                    doc = cls.__doc__
                    if doc is None:
                        doc = " "
                    else:
                        doc = doc.strip().replace("\n", "")

                    doc = re.sub(r"\s+", " ", doc)
                    result.append(
                        '|`%s.%s`| | | %s |' % (module_name.split('.')[-2], cls.__name__, doc))
                    try:
                        for opt in cls.options():
                            doc = opt.get_docstring()
                            if doc is None:
                                doc = " "
                            result.append(
                                '| | `%s` | %s | %s' % (opt.get_name(), opt.is_required(), doc))
                    except AttributeError:
                        pass
        return os.linesep.join(result)

    @staticmethod
    def __create_info_documentation():
        base_path = RuntimeOptions().base_path()
        searchpath = os.path.join(base_path, 'hardening', 'info')
        result = [
            '|Substring| Replacement',
            '|-|-'
        ]

        for root, _, files in os.walk(searchpath):
            for code_file in [f for f in files if f.endswith(".py")]:
                module_name = os.path.join(root.replace(base_path + os.sep, ""),
                                           code_file[:-3]).replace('/', '.')
                class_name = module_name.split('.')[-1].decode()

                pkg = importlib.import_module(module_name)

                cls = getattr(pkg, class_name)

                if not inspect.isclass(cls):
                    # pylint: disable=superfluous-parens
                    print("omitting %(class)s" % {'class': class_name})
                    continue

                obj = cls()

                if not hasattr(obj, "keyword"):
                    # pylint: disable=superfluous-parens
                    print("%(class)s has no keyword method" %
                          {'class': class_name})
                    continue

                keyword = cls.keyword()

                Documentation.create_interpolate_docs(cls, keyword, result)
                Documentation.create_getter_docs(cls, keyword, result)

        return os.linesep.join(result)

    @staticmethod
    def create_getter_docs(info_cls, keyword, result):
        for name, method in inspect.getmembers(info_cls, inspect.ismethod):
            if name.startswith("get_"):
                # noinspection PyDeprecation
                argspec = inspect.getargspec(method)
                parts = ":".join(
                    ["<" + p + ">" for p in argspec.args if p != 'self'])
                if len(parts) > 0:
                    parts = ":" + parts
                interpolated_string = "`info:%s:%s%s`" % (
                    keyword, name[4:], parts)
                result.append("| %s | %s" % (interpolated_string,
                                             str(method.__doc__).replace("\n", " ").strip()))

    @staticmethod
    def create_interpolate_docs(info_cls, keyword, result):
        if hasattr(info_cls, "interpolate"):
            method = info_cls.interpolate
            # noinspection PyDeprecation
            argspec = inspect.getargspec(method)
            parts = ":".join([p for p in argspec.args if p != 'self'])
            interpolated_string = "`info:%s:<%s>`" % (keyword, parts)
            result.append("| %s | %s" % (interpolated_string,
                                         str(method.__doc__).replace("\n", " ").strip()))

    def get_documentation(self):
        return Documentation.__get_generic_documentation() % (
            RuntimeOptions().get_help_text(),
            self.__create_info_documentation(),
            Documentation.__create_util_documentation())
