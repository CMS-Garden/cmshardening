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

import grp


class Group(object):
    """ provides an interface to the `/etc/group` file

    Normally, you could use the `grp` module, which this class itself does.
    But this does not work on any operating system. If you don't to rely on
    platform specific modules, please use this class ;-)
    """

    def has_group_entry(self, name):
        """ checks if a group with a certain name exists

        @param name: name of the group
        @return `True` if a group with the given name exists; `False` otherwise
        """
        try:
            self.get_group_entry(name)
            return True
        except KeyError:
            return False

    @staticmethod
    def get_group_entry(name):
        """ returns a tuple which describes a group

        The returned tuple contains the following entries:
        | Index	| Attribute	| Meaning |
        | ----- | --------- | ------- |
        | 0 | ``gr_name`` | the name of the group |
        | 1 | ``gr_passwd`` | the (encrypted) group password; often empty |
        | 2 | ``gr_gid`` | the numerical group ID |
        | 3 | ``gr_mem`` | all the group member's user names |

        If no group by the given name exists, a KeyError is raised

        @param name: name of the group
        @return tuple as described above
        """
        return grp.getgrnam(name)

    def get_gid(self, name):
        """ returns the id of the group with the given name

        If no group by the given name exists, a KeyError is raised

        @param name: name of the group
        @return id of the group
        """
        return self.get_group_entry(name)[2]
