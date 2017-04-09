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


namespace php\tests\parser;

require_once 'core/bootstrap.php';
use \php\parser\Typo3ConfigParser;
use \PHPUnit_Framework_TestCase;
use \php\core\configuration\Configuration;
use \Exception;

class Typo3ConfigParserTest extends PHPUnit_Framework_TestCase
{
    protected $configparser;

    public function setUp()
    {
        Configuration::getInstance()->setProperty("typo3.Options.RootPath", ROOT_PATH . "tests\\samples\\Typo3\\");
        Configuration::getInstance()->setProperty("typo3.Options.ConfigurationFolder", ROOT_PATH . "tests/samples/Typo3/typo3conf/");

        // create config file from backup file
        copy(ROOT_PATH . "tests/samples/Typo3/typo3conf/" . 'LocalConfiguration.php_backup', ROOT_PATH . "tests/samples/Typo3/typo3conf/" . 'LocalConfiguration.php');

        try {
            $this->configparser = Typo3ConfigParser::getInstance();
        } catch (Exception $e) {
            echo $e->getMessage() . PHP_EOL;
            return;
        }
    }

    public function testGetProperty()
    {
        $this->assertEquals("0", $this->configparser->getProperty("BE/debug"));
        $this->assertEquals("typo3", $this->configparser->getProperty("DB/database"));
        $this->assertEquals(null, $this->configparser->getProperty("NOT/Existent"));
    }

    public function testSetProperty()
    {
        $val = rand(0, 2);
        $this->configparser->setProperty("BE/lockSSL", $val);
        $this->assertEquals($val, $this->configparser->getProperty("BE/lockSSL"));
    }

    public function testRemoveProperty()
    {
        $this->configparser->removeProperty("DB/socket");
        $this->assertEquals(null, $this->configparser->getProperty("DB/socket"));
    }

    public function testRemoveNotExistingProperty()
    {
        $this->configparser->removeProperty("NOT/Existent");
    }

    public function tearDown()
    {
        $this->configparser = NULL;
        unlink(ROOT_PATH . "tests/samples/Typo3/typo3conf/" . 'LocalConfiguration.php');
    }
}