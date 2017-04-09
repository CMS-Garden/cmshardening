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

import functools


def singleton(cls):
    """Decorator which implements the Singleton pattern

    The implementation of this class is derived from
    [https://wiki.python.org/moin/PythonDecoratorLibrary#Singleton]

    Usage of this class is simple:
    ```python
    @core.singleton
    class MyClass(object):
        pass
    ```
    """

    cls.__new_original__ = cls.__new__

    @functools.wraps(cls.__new__)
    def singleton_new(singleton_cls, *args, **kw):
        instance = singleton_cls.__dict__.get('__it__')
        if instance is not None:
            return instance

        # remove class object from args
        args = args[1:]

        singleton_cls.__it__ = instance = singleton_cls.__new_original__(
            singleton_cls, *args, **kw)
        instance.__init_original__(*args, **kw)
        return instance

    cls.__new__ = classmethod(singleton_new)
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls
