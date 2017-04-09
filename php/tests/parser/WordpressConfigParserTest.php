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
use \php\parser\WordpressConfigParser;
use \php\core\configuration\Configuration;
use \PHPUnit_Framework_TestCase;

class WordpressConfigParserTest extends PHPUnit_Framework_TestCase
{
    protected $configparser;
    protected static $rootPath = ROOT_PATH . "tests/samples/Wordpress/";
    protected static $configFile = "wp-config-sample.php_";

    public static function getConfigFile()
    {
        return self::$rootPath . self::$configFile;
    }

    public static function createConfigFile()
    {
        $configFile = self::getConfigFile();
        $configFileBackup = $configFile . "backup";
        copy($configFileBackup, self::getConfigFile());
        return $configFile;
    }

    public function setUp()
    {
        self::createConfigFile();
        $this->configparser = WordpressConfigParser::fromFile(self::getConfigFile());
    }

    public function testGetProperty()
    {
        $this->assertEquals("database_name_here", $this->configparser->getProperty("DB_NAME"));
        $this->assertEquals("username_here", $this->configparser->getProperty("DB_USER"));
        $this->assertEquals("password_here", $this->configparser->getProperty("DB_PASSWORD"));
        $this->assertEquals("put your unique phrase here", $this->configparser->getProperty("AUTH_KEY"));
        $this->assertEquals("multiple3", $this->configparser->getProperty("MULTIPLE"));
    }

    public function testGetPropertyTypes()
    {
        $this->assertEquals(false, $this->configparser->getProperty("WP_DEBUG"));
        $this->assertEquals(null, $this->configparser->getProperty("NONEEXISTING"));
        $this->assertEquals(4, $this->configparser->getProperty("integer"));
        $this->assertEquals(4.33, $this->configparser->getProperty("float"));
        $this->assertEquals(true, $this->configparser->getProperty("boolean"));
    }

    public function testSetProperty()
    {
        $newValue = "newValue";
        $this->configparser->setProperty("DB_NAME", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("DB_NAME"));

        $this->configparser->setProperty("SOMETHINGNEW", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("SOMETHINGNEW"));

        $this->configparser->setProperty("MULTIPLE", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("MULTIPLE"));
    }

    public function testSetPropertyTypes()
    {
        $newValue = true;
        $this->configparser->setProperty("SOMETHINGNEW", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("SOMETHINGNEW"));

        $newValue = 15;
        $this->configparser->setProperty("SOMETHINGNEW", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("SOMETHINGNEW"));

        $newValue = 3.91;
        $this->configparser->setProperty("SOMETHINGNEW", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("SOMETHINGNEW"));
    }

    public function testRemoveProperty()
    {
        $this->configparser->removeProperty("DB_NAME");
        $this->assertEquals(null, $this->configparser->getProperty("DB_NAME"));

        $this->configparser->removeProperty("SOMETHINGELSE");
        $this->assertEquals(null, $this->configparser->getProperty("SOMETHINGELSE"));

        $this->configparser->removeProperty("MULTIPLE");
        $this->assertEquals(null, $this->configparser->getProperty("MULTIPLE"));
    }

    public function testSanitizeValue()
    {
        $newValue = "abc\"def'ghi\\jklm/no";
        $this->configparser->setProperty("SOMETHINGNEW", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("SOMETHINGNEW"));
        $newValue = 'abc\"def\'ghi\\jklm/no';
        $this->configparser->setProperty("SOMETHINGNEW2", $newValue);
        $this->assertEquals($newValue, $this->configparser->getProperty("SOMETHINGNEW2"));
    }

    public function testMassiveAdd()
    {
        $times = 100;
        while ($times > 0) {
            $times--;
            $this->configparser->setProperty("DB_USER-$times", "somevalue-$times");
        }
        // ConfigParser has to be created newly to fetch the new content of the files
        $configparser = WordpressConfigParser::fromFile(self::getConfigFile());
        $this->assertEquals("somevalue-$times", $configparser->getProperty("DB_USER-$times"));
    }

    public function testReload()
    {
        $property = "DB_USER";

        // Assert that property does not contain value (Precondition).
        $value = "value";
        $this->assertNotEquals($this->configparser->getProperty($property), $value);

        // Write value
        $this->configparser->setProperty($property, $value);
        $this->assertEquals($this->configparser->getProperty($property), $value);

        // Reload and test whether property contains still value (Postcondition)
        $this->configparser->loadConfigFile();
        $this->assertEquals($this->configparser->getProperty($property), $value);
    }

    public function tearDown()
    {
        unlink(self::createConfigFile());
    }
}