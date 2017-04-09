#!/usr/bin/env python
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


import inspect
import os
import sys

from hardening import io, core
from hardening.core.Documentation import Documentation
from hardening.scheduler import Scheduler


def main():
    core.RuntimeOptions()

    if core.RuntimeOptions().is_documentation_enabled():
        print(Documentation().get_documentation())
        sys.exit(0)

    if os.getuid() != 0:
        print((_("This tool MUST be run with root privileges, "
                 "obtained using sudo!")))
        sys.exit(-1)

    if os.getlogin() == 'root':
        print((_("You should not run this tool using the root account\n"
                 "Instead, you should use sudo!")))

    io.create_writer().display_message(
        message=_(u" ___ ___ ___   ___ __  __ ___   ___\n"
                  u"| _ ) __|_ _| / __|  \/  / __| |_  )\n"
                  u"| _ \__ \| | | (__| |\/| \__ \_ / /\n"
                  u"|___/___/___(_)___|_|  |_|___(_)___|\n"), hyphenate=False)
    io.create_writer().display_message(
        message=_(u"This script aims to harden some Content Management Systems (CMS) "
                  u"to increase the security. Among others the configuration file(s) "
                  u"of the CMS is altered to make use of a more secure configuration. "
                  u"The script can be applied to an initial installed and configured "
                  u"CMS as well as to a long-lived installation.\n For every "
                  u"automatic altered file there will be a backup of the original "
                  u"state in the corresponding backup directory."),
        headline=_(u"Introduction"))
    io.create_writer().display_message("", hyphenate=False)

    io.create_writer().display_message(
        message=_(u"The following adjustments will alter your system.\n"
                  u"There is no guarantee the altered components are still "
                  u"working as expected.\nPlease use this script carefully "
                  u"and read up about the implication of the changes. "
                  u"Although these hardening steps increase the security of "
                  u"your system, there still might exist vulnerabilities due "
                  u"to implementation error of certain components. \n"
                  u"The configuration suggested by this script is aimed for "
                  u"the test environment described in "
                  u"'Sicherheitsstudie Content Management Systeme 2.0'. "
                  u"Other environments may require a different configuration."),
        headline=_(u"Attention!"))
    io.create_writer().display_message("", hyphenate=False)

    if not io.create_writer().prompt_user_yesno(
            default=_("no"),
            caption=_("WARNING --- WARNING --- WARNING"),
            message=_(u"Be aware that this tool may impair your system if you are concurrently "
                      u"using a system management suite, such as PLESK or CONFIXX !!!"
                      u"\u00a7{n}\u00a7{n}"
                      u"You should only continue if you are are sure that no such tools are "
                      u"running!\u00a7{n}\u00a7{n}"
                      u"Do you really want to continue?")):
        sys.exit(0)

    scheduler = Scheduler()
    try:
        scheduler.run_hardening_modules()
    except SystemExit:
        io.create_writer().display_message(
            headline=_("Hardening aborted!!!!"),
            message=_("The hardening was stopped due to user request or unexpected behaviour."
                      " No hardening effects were applied.")
        )
        return

    if core.RuntimeOptions().is_log_enabled():
        # noinspection PyBroadException
        try:
            log_location = core.RuntimeOptions().logfile().name
        except ValueError:
            log_location = core.RuntimeOptions().logfile()

        if core.ChangeLog().has_items_to_save():
            core.ChangeLog().store_log()

            io.create_writer().display_message(
                headline=_("Log location"),
                message=_(u"Your hardening log was written to '%(location)s'")
                % {'location': log_location})
        else:
            if os.path.isfile(log_location):
                os.unlink(log_location)
            io.create_writer().display_message(
                headline=_("Log location"),
                message=_(u"No hardening log was created because no changes are necessary."))

    if not core.RuntimeOptions().silent_mode():
        io.create_writer().display_message(
            headline=_("Hardening finished!!!!"),
            message=_(u"If you're also planning to harden one of WORDPRESS, JOOMLA "
                      u"or TYPO3, you should run the PHP-part of this tool:"
                      u"\u00a7{n}\u00a7{n}"
                      u"  cd ../php && php index.php\u00a7{n}\u00a7{n}"
                      u"Please check that all your services (apache, sshd, etc.) are running "
                      u"as expected. If they do, you should restart your computer to make "
                      u"sure the hardening effects are applied.\u00a7{n}\u00a7{n}"
                      u"Otherwise, you should restore the old configuration "
                      u"from the backup files.\u00a7{n}")
        )


def get_language_file(language_code):
    default_language = "en"
    filename_pattern = "lang_%(locale)s.ini"
    base_path = os.path.dirname(inspect.getfile(inspect.currentframe()))

    for lang in (language_code, language_code.split("_")[0], default_language):
        filename = os.path.join(base_path, os.pardir, "python", "lang",
                                filename_pattern % {'locale': lang})
        if os.path.exists(filename):
            return filename
    return None


def print_usage():
    pass


if __name__ == '__main__':
    main()
