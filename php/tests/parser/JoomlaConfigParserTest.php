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
use php\core\Util;
use \php\parser\JoomlaConfigParser;
use \php\core\configuration\Configuration;
use \PHPUnit_Framework_TestCase;
use \Exception;

class JoomlaConfigParserTest extends PHPUnit_Framework_TestCase
{

    public function configFileProvider()
    {
        return array(
            array(ROOT_PATH . "tests/samples/Joomla/configuration_windows.php_"),
            array(ROOT_PATH . "tests/samples/Joomla/configuration_linux.php_")
        );
    }

    public static function createConfigFile($configFile)
    {
        $configFileBackup = $configFile . "backup";
        copy($configFileBackup, $configFile);
        return $configFile;
    }

    public function setUp()
    {
        foreach ($this->configFileProvider() as $configFile)
        {
            self::createConfigFile($configFile[0]);
        }
    }

    public function tearDown()
    {
        foreach ($this->configFileProvider() as $configFile)
        {
            unlink($configFile[0]);
        }
    }

    public function testInit_WhenConfigurationInvalid_ThrowException()
    {
        $this->setExpectedException("Exception");
        $configFile = ROOT_PATH . "tests/samples/Joomla/configuration_invalid.php_backup";
        // The syntax of the file should be false.
        $this->assertEquals(Util::check_php_syntax($configFile), false);
        // An exception should be thrown when loading the file.
        JoomlaConfigParser::fromFile($configFile);
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testGetProperty($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        $this->assertEquals("jce", $configparser->getProperty("editor"));
        $this->assertEquals("joomla", $configparser->getProperty("db"));
        $this->assertEquals("https://help.joomla.org/proxy/index.php?option=com_help&keyref=Help{major}{minor}:{keyref}", $configparser->getProperty("helpurl"));
        $this->assertEquals(false, $configparser->getProperty("WP_DEBUG"));
        $this->assertEquals(null, $configparser->getProperty("NONEEXISTING"));
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testGetPropertyWithoutQuotes($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        $this->assertEquals("1", $configparser->getProperty("without_quotes"));
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testSetProperty($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        $newValue = "newValue";
        $configparser->setProperty("db", $newValue);
        $this->assertEquals($newValue, $configparser->getProperty("db"));

        $configparser->setProperty("somethingelse", $newValue);
        $this->assertEquals($newValue, $configparser->getProperty("somethingelse"));
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testSetProperty_DoesNotCreateDuplicateEntry_WhenSameValue($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        // Write entry.
        $value = "1";
        $configparser->setProperty("debug", $value);
        $this->assertEquals($value, $configparser->getProperty("debug"));

        // Write same entry again with same value.
        $configparser->loadConfigFile();
        $configparser->setProperty("debug", $value);

        // Assert that no syntax-errors exists within config-file.
        exec('php -l ' . $configFile, $arrMsgError, $nCodeError);
        $this->assertEquals($nCodeError, 0); // No errors.
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testSetProperty_DoesNotCreateDuplicateEntry_WhenDifferentValue($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        // Write entry.
        $value = "1";
        $configparser->setProperty("debug", $value);
        $this->assertEquals($value, $configparser->getProperty("debug"));

        // Write same entry again with different value.
        $configparser->loadConfigFile();
        $newValue = "0";
        $configparser->setProperty("debug", $newValue);

        // Assert that no syntax-errors exists within config-file.
        exec('php -l ' . $configFile, $arrMsgError, $nCodeError);
        $this->assertEquals($nCodeError, 0); // No errors.
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testRemoveProperty($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        $configparser->removeProperty("db");
        $this->assertEquals(null, $configparser->getProperty("db"));

        $configparser->removeProperty("somethingelse");
        $this->assertEquals(null, $configparser->getProperty("somethingelse"));
    }

    /**
     * @dataProvider configFileProvider
     * @param $configFile string the path to the config file
     */
    public function testSanitizeValue($configFile)
    {
        $configparser = JoomlaConfigParser::fromFile($configFile);
        $newValue = "abc\"def'ghi\\jklm/no";
        $configparser->setProperty("somethingelse", $newValue);
        $this->assertEquals($newValue, $configparser->getProperty("somethingelse"));
        $newValue = 'abc\"def\'ghi\\jklm/no';
        $configparser->setProperty("somethingelse2", $newValue);
        $this->assertEquals($newValue, $configparser->getProperty("somethingelse2"));
    }
}