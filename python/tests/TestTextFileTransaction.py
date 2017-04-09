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
from hardening.storage import TextFileTransaction
from hardening.core import RuntimeOptions


class TextTextFileTransactionTestCase(unittest.TestCase):
    """
    Tests different changes for text files, e.g. deleting, appending a ling...
    """

    def testBackupWithoutModification(self):
        self.transaction().prepare_commit()
        self.transaction().commit()
        self.assertTrue(os.path.exists(self.filename()))

        # backups are only written if the file is modified
        self.assertFalse(os.path.exists(self.transaction().backup_path()))

    def testBackupWithModification(self):
        self.transaction().append_line(self.testline())
        self.transaction().prepare_commit()
        self.transaction().commit()
        self.assertTrue(os.path.exists(self.filename()))
        self.assertTrue(os.path.exists(self.transaction().backup_path()))

        original = open(self.filename())
        backup = open(self.transaction().backup_path())

        original_lines = original.readlines()
        backup_lines = backup.readlines()

        # append the added line
        backup_lines[-1] += os.linesep
        backup_lines.append(self.testline() + os.linesep)
        diff = difflib.unified_diff(original_lines, backup_lines)

        self.assertEquals(len(list(diff)), 0)

        backup.close()
        original.close()

    def testFlush1(self):
        self.transaction().flush()

        self.transaction().prepare_commit()
        self.transaction().commit()

        with open(self.filename(), "r") as f:
            lines = f.readlines()
            self.assertEquals(len(lines), 0)

    def testAppendUniqueLine(self):
        self.transaction().flush()
        self.transaction().append_unique_line(self.testline())
        self.transaction().append_unique_line(self.testline())

        self.transaction().prepare_commit()
        self.transaction().commit()

        with open(self.filename(), "r") as f:
            lines = f.readlines()
            self.assertEquals(len(lines), 1)
            self.assertEquals(lines[0], self.testline() + os.linesep)

    def testRollback1(self):
        self.transaction().append_line(self.testline())
        self.assertTrue(os.path.exists(self.transaction().tmpname()))
        self.assertFalse(os.path.exists(self.transaction().backup_path()))

        self.transaction().rollback()
        self.assertFalse(os.path.exists(self.transaction().tmpname()))
        self.assertFalse(os.path.exists(self.transaction().backup_path()))

    def testDelete(self):
        self.transaction().delete()
        self.transaction().prepare_commit()
        self.transaction().commit()
        self.assertFalse(os.path.exists(self.filename()))
        self.assertTrue(os.path.exists(self.transaction().backup_path()))
        with open(self.transaction().backup_path()) as f:
            self.assertEquals(f.read(), self.teststring())

    def testMissingOriginal(self):
        self.transaction().prepare_commit()
        self.transaction().commit()

        # generate a filename of the missing file
        missing = tempfile.NamedTemporaryFile(delete=True)
        self.__filename = missing.name
        missing.close()

        # ensure the file is missing
        self.assertFalse(os.path.exists(self.__filename))

        # create a transaction on the missing file
        self.__transaction = TextFileTransaction(self.__filename)
        self.__transaction.begin()
        self.__transaction.add_lines(*os.linesep.split(self.teststring()))
        self.transaction().prepare_commit()
        self.transaction().commit()

        # ensure the file is not missing anymore
        self.assertTrue(os.path.exists(self.__filename))

        # ensure the backup is missing
        self.assertFalse(os.path.exists(self.transaction().backup_path()))

    def testMissingOriginalPath(self):
        self.transaction().prepare_commit()
        self.transaction().commit()

        # generate a filename of the missing directory
        missing = tempfile.NamedTemporaryFile(delete=True)
        self.__filename = os.path.join(
            missing.name, os.path.basename(missing.name))
        missing.close()

        # ensure the file is missing
        self.assertFalse(os.path.exists(self.__filename))

        # create a transaction on the missing file
        self.__transaction = TextFileTransaction(self.__filename)
        self.__transaction.begin()
        self.__transaction.add_lines(*os.linesep.split(self.teststring()))
        self.transaction().prepare_commit()
        self.transaction().commit()

        # ensure the file is not missing anymore
        self.assertTrue(os.path.exists(self.__filename))

        # ensure the backup is missing
        self.assertFalse(os.path.exists(self.transaction().backup_path()))

    def setUp(self):
        self.__teststring = """
Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium,
totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae
dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit,
sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam
est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius
modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima
veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea
commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil
molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum
deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non
provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum
fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis
est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis
voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis
aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non
recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus
maiores alias consequatur aut perferendis doloribusasperiores repellat.
        """
        RuntimeOptions().enable_silent_mode()
        origfile = tempfile.NamedTemporaryFile(delete=False)
        self.__filename = origfile.name
        origfile.write(self.__teststring)
        origfile.close()
        self.__transaction = TextFileTransaction(self.__filename)
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

    @staticmethod
    def testline():
        return "hello, world"
