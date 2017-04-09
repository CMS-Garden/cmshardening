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

from hardening import utils, constants, io


@utils.ModuleSettings()
class LeaveModule(utils.HardeningUtil):
    """
    this util displays a message when a module has finished all its actions and can be closed
    """

    def __run__(self):
        assert self.get_runtimeinfo(constants.OPTION_MODULE) is not None
        io.create_writer().display_headline(
            (_("Leaving module %(module)s")
             % {'module': self.get_runtimeinfo(constants.OPTION_MODULE)})
        )

utils.HardeningUtil.register(LeaveModule)
