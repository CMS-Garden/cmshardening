<?php
/* This file is part of BSICMS2.
 *
 * BSICMS2 is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


namespace php\tests\transaction;

require_once 'core/bootstrap.php';
use Exception;
use \php\parser\WordpressConfigParser;
use php\tests\parser\WordpressConfigParserTest;
use \php\core\storage\TransactionManager;
use \php\core\configuration\Configuration;
use \PHPUnit_Framework_TestCase;

class FileTransactionTest extends PHPUnit_Framework_TestCase
{
    private $tm;

    private $configFile;

    public function setUp()
    {
        $this->configFile = $this->createConfigFile();
        $this->tm = TransactionManager::getInstance();
    }

    public function tearDown()
    {
        unlink($this->getConfigFile());
        // delete all created backupfiles
        $this->tm->rollBackAllTransactions();
        foreach ($this->tm->getTransactions() as $transaction) {
            $file = $transaction->getFileBackup();
            if (file_exists($file)) {
                chmod($file, 0777);
                unlink($file);
            }
        }
        $this->tm->clearTransactions();
    }

    public function testBegin_WhenOriginalFileNotReadable_Fails()
    {
        $transaction = $this->tm->createTransaction("not-existing-file", "FILE");
        $transaction->begin();
        $this->assertFileNotExists($transaction->getFileBackup());
    }

    /**
     * @expectedException Exception
     */
    public function testBegin_WhenBackupFileAlreadyExists_Fails()
    {
        $wordpressconfigfile = $this->getConfigFile();
        $transaction = $this->tm->createTransaction($wordpressconfigfile, "FILE");
        $file_backup = $transaction->getFileBackup();
        touch($file_backup);
        $transaction->begin();
    }

    /**
     * @expectedException Exception
     */
    public function testBegin_WhenBackupLocationNotWriteable_Fails()
    {
        $wordpressconfigfile = $this->getConfigFile();
        $transaction = $this->tm->createTransaction($wordpressconfigfile, "FILE");
        $file_backup = $transaction->getFileBackup();
        touch($file_backup);
        chmod($file_backup, 0);
        $transaction->begin();
    }

    private function createConfigFile()
    {
        return WordpressConfigParserTest::createConfigFile();
    }

    private function getConfigFile()
    {
        return WordpressConfigParserTest::getConfigFile();
    }
}