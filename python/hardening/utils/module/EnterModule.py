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

from hardening import utils, constants, io, core


@utils.ModuleSettings(
    options=[
        utils.UtilOption(constants.OPTION_MODULEMETA, required=False,
                         docstring="meta information of the current module")
    ]
)
class EnterModule(utils.HardeningUtil):
    """
    this util displays informational messages for the module that is currently being loaded
    """

    def __setup__(self):
        assert self.get_runtimeinfo(constants.OPTION_MODULE) is not None

        io.create_writer().display_headline(
            (_("Collecting information required for module %(module)s")
             % {'module': self.get_runtimeinfo(constants.OPTION_MODULE)})
        )

    def __run__(self):
        assert self.get_runtimeinfo(constants.OPTION_MODULE) is not None

        io.create_writer().display_headline(
            _("Running module %(module)s")
            % {'module': self.get_runtimeinfo(constants.OPTION_MODULE)})
        self.display_module_headline()

    def display_module_headline(self):
        caption = self.get_module_metainfo(constants.CONFIG_CAPTION)
        description = self.get_module_metainfo(constants.CONFIG_DESCRIPTION)
        if caption is not None:
            io.create_writer().display_message(headline=caption, message=description)

    def get_module_metainfo(self, opt):
        meta = self.get_option(constants.OPTION_MODULEMETA)
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


utils.HardeningUtil.register(EnterModule)
