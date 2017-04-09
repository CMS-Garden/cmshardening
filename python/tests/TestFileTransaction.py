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

import unittest
import tempfile
import os
import difflib
from hardening.storage import FileTransaction
from hardening.core import RuntimeOptions


class TestFileTransactionTestCase(unittest.TestCase):
    """
    Tests file transaction functions like delete and backup
    """

    def testBackup(self):
        self.transaction().prepare_commit()
        self.transaction().commit()
        self.assertTrue(os.path.exists(self.filename()))
        self.assertFalse(os.path.exists(self.transaction().backup_path()))

        original = open(self.filename())

        diff = difflib.unified_diff(original.readlines(),
                                    [x + os.linesep for x in self.teststring().split(os.linesep)])
        self.assertEquals(len(list(diff)), 0)

        original.close()

    def testDelete(self):
        self.transaction().delete()
        self.transaction().prepare_commit()
        self.transaction().commit()
        self.assertFalse(os.path.exists(self.filename()))
        self.assertTrue(os.path.exists(self.transaction().backup_path()))
        with open(self.transaction().backup_path()) as f:
            self.assertEquals(f.read(), self.teststring() + os.linesep)

    def setUp(self):
        self.__teststring = """
Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium,
totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae
dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit,
sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam
est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam
eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima
veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea
commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam
nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum
deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non
provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum
fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis
est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis
voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis
aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non
recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus
maiores alias consequatur aut perferendis doloribus asperiores repellat.
        """
        RuntimeOptions().enable_silent_mode()
        origfile = tempfile.NamedTemporaryFile(delete=False)
        self.__filename = origfile.name
        origfile.write(self.__teststring + os.linesep)
        origfile.close()
        self.__transaction = FileTransaction(self.__filename)
        self.__transaction.begin()

    def tearDown(self):
        if os.path.exists(self.__filename):
            os.unlink(self.__filename)
        self.__filename = None
        self.__transaction = None

    def transaction(self):
        return self.__transaction

    def filename(self):
        return self.__filename

    def teststring(self):
        return self.__teststring
