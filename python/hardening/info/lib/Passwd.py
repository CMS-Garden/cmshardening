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

import pwd


class Passwd(object):
    """ provides an interface to the `/etc/passwd` file

    Normally, you could use the `pwd` module, which this class itself does. But
    this does not work on any operating system. If you don't to rely on
    platform specific modules, please use this class ;-)
    """

    def has_passwd_entry(self, name):
        """ checks if a user with a certain name exists

        @param name: name of the user
        @return `True` if a user with the given name exists; `False` otherwise
        """
        try:
            self.get_passwd_entry(name)
            return True
        except KeyError:
            return False

    @staticmethod
    def get_passwd_entry(name):
        """ returns a tuple which describes a user

        The returned tuple contains the following entries:

        | Index | Attribute | Meaning |
        | ----- | --------- | ------- |
        | 0 | ``pw_name`` | Login name |
        | 1 | ``pw_passwd`` | Optional encrypted password |
        | 2 | ``pw_uid`` | Numerical user ID |
        | 3 | ``pw_gid`` | Numerical group ID |
        | 4 | ``pw_gecos`` | User name or comment field |
        | 5 | ``pw_dir`` | User home directory |
        | 6 | ``pw_shell`` | User command interpreter |

        If no user by the given name exists, a KeyError is raised

        @param name: name of the user
        @return tuple as described above
        """
        return pwd.getpwnam(name)

    def get_uid(self, name):
        """ returns the id of the user with the given name

        If no user by the given name exists, a KeyError is raised

        @param name: name of the user
        @return id of the user
        """
        return self.get_passwd_entry(name)[2]
