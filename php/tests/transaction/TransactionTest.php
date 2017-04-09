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
use \php\parser\WordpressConfigParser;
use php\tests\parser\WordpressConfigParserTest;
use \php\core\storage\TransactionManager;
use \php\core\configuration\Configuration;
use \PHPUnit_Framework_TestCase;

class TransactionTest extends PHPUnit_Framework_TestCase
{
    private $tm;

    public function setUp()
    {
        $this->createConfigFile();
        $this->tm = TransactionManager::getInstance();
    }

    public function tearDown()
    {
        unlink($this->getConfigFile());
        // delete all created backup files
        $this->tm->rollBackAllTransactions();
        foreach ($this->tm->getTransactions() as $transaction) {
            $file = $transaction->getFileBackup();
            if (file_exists($file))
                unlink($file);
        }
        $this->tm->clearTransactions();
    }

    public function testBeginTransaction()
    {
        $wordpressconfigfile = $this->getConfigFile();
        $transaction = $this->tm->createTransaction($wordpressconfigfile, "FILE");
        $transaction->begin();
        $this->assertFileExists($transaction->getFileBackup());
    }


    /**
     *  Try to create a transaction with an unknown type (valid would be e.g. "FILE")
     */
    public function testCreatePoorTransaction()
    {
        $this->setExpectedException("Exception");
        $this->tm->createTransaction("", "foobar2");
    }

    public function testCommitTransaction()
    {
        $wordpressconfigfile = $this->getConfigFile();
        $transaction = $this->tm->createTransaction($wordpressconfigfile, "FILE");
        $transaction->begin();
        $this->assertFileExists($transaction->getFileBackup());

        $configparser = $this->getNewParser();
        $configparser->setProperty("DB_USER", "somevalue");
        $transaction->commit();
        // ConfigParser has to be created newly to fetch the new content of the files
        $configparser->loadConfigFile();
        $this->assertEquals("somevalue", $configparser->getProperty("DB_USER"));

        $this->assertFileNotEquals($transaction->getFileBackup(), $transaction->getFileOriginal());
    }

    public function testRollbackTransaction()
    {
        $wordpressconfigfile = $this->getConfigFile();
        $transaction = $this->tm->createTransaction($wordpressconfigfile, "FILE");
        $transaction->begin();
        $this->assertFileExists($transaction->getFileBackup());

        $configparser = $this->getNewParser();
        $configparser->setProperty("somekey", "somevalue");
        $transaction->rollback();
        $this->assertFileEquals($transaction->getFileBackup(), $transaction->getFileOriginal());
    }

    private function getConfigFile()
    {
        return WordpressConfigParserTest::getConfigFile();
    }

    private function createConfigFile()
    {
        return WordpressConfigParserTest::createConfigFile();
    }

    private function getNewParser()
    {
        return WordpressConfigParser::fromFile(WordpressConfigParserTest::getConfigFile());
    }
}