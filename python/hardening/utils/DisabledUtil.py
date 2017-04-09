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

from hardening import utils, constants, core


@utils.ModuleSettings()
class DisabledUtil(utils.HardeningUtil):
    """
    displays a message when the hardening-util is not enabled due to run-if conditions checks
    failing
    """

    def __run__(self):
        assert self.get_runtimeinfo(constants.OPTION_UTIL) is not None

        cause = ""
        # noinspection PyBroadException
        try:
            cause = " " + \
                str(self.get_runtimeinfo(constants.OPTION_CAUSE, interpolate=False))
        # pylint: disable=bare-except
        except:
            pass
        core.LogManager().get_logger().info(
            (_("The util %(util)s is disabled due to the precondition%(cause)s.")
             % {'util': self.get_runtimeinfo(constants.OPTION_UTIL),
                'cause': cause}))


utils.HardeningUtil.register(DisabledUtil)
