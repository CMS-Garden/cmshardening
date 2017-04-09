#!/usr/bin/env python
import os

PROGRAM_NAME = "BSICMS2"

COPYRIGHT_TEXT = \
    """# This file is part of {program_name}.
#
# {program_name} is free software: you can redistribute it and/or modify
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
"""


def transform(text):
    if "This file is part of" in text:
        return None

    if text.startswith("#!"):
        parts = text.split(os.linesep)
        shebang = parts[0] + "\n"
        text = os.linesep.join(parts[1:])
    else:
        shebang = ""

    copyright_info = COPYRIGHT_TEXT.format(program_name=PROGRAM_NAME).strip()

    return shebang + copyright_info + os.linesep + os.linesep + text


def update_copyright():
    for root, _, files in os.walk(os.getcwd()):
        for _file in [os.path.join(root, x)
                      for x in files if x.endswith('.py')]:
            with open(_file, 'r') as code_file:
                newtext = transform(code_file.read())
            if newtext:
                # pylint: disable=superfluous-parens
                print("updating %s" % _file)
                with open(_file, 'w') as code_file:
                    code_file.write(newtext)
            else:
                # pylint: disable=superfluous-parens
                print("omitting %s" % _file)


if __name__ == '__main__':
    update_copyright()
