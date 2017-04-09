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

from hardening import utils, storage, constants


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_SERVICEACTION, required=True,
                         docstring="specifies what must be done with the service. "
                                   "must be one of `enable`, `disable`, `start` or `stop`")
    ],
    required_transaction=storage.ServiceTransaction
)
class ConfigureService(utils.HardeningUtil):
    """
    this class is used to enable, disable, start or stop a service
    """

    __SERVICEACTION_ENABLE = "enable"
    __SERVICEACTION_DISABLE = "disable"
    __SERVICEACTION_START = "start"
    __SERVICEACTION_STOP = "stop"

    __valid_actions = {
        __SERVICEACTION_ENABLE: storage.ServiceTransaction.enable_service,
        __SERVICEACTION_DISABLE: storage.ServiceTransaction.disable_service,
        __SERVICEACTION_START: storage.ServiceTransaction.start_service,
        __SERVICEACTION_STOP: storage.ServiceTransaction.stop_service
    }

    # pylint: disable=unused-argument
    def __init__(self, *args, **kwargs):
        super(ConfigureService, self).__init__(**kwargs)

        if self.get_option(
                constants.OPTION_SERVICEACTION) not in self.__valid_actions.keys():
            raise SyntaxError(_("invalid service action: '%(action)s'")
                              % {'action': self.get_option(constants.OPTION_SERVICEACTION)})

        self.__service_action = self.__valid_actions[
            self.get_option(constants.OPTION_SERVICEACTION)]

    def __run__(self):
        self.__service_action(self.transaction())
