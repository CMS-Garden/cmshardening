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


namespace parser;

require_once 'core/bootstrap.php';
use php\parser\PHPUserIniParser;
use PHPUnit_Framework_TestCase;

class PHPUserIniParserTest extends PHPUnit_Framework_TestCase
{
    private $sampleNotExistingUserIni = TEST_PATH . 'samples/PHPUserINI/.user2.ini';
    private $sampleExistingUserIni = TEST_PATH . 'samples/PHPUserINI/.user.ini';

    public function setUp()
    {
        // recover the existing user.ini from the backup-file
        copy($this->sampleExistingUserIni . '_backup', $this->sampleExistingUserIni);

    }

    public function testGetPropertyEmpty()
    {
        $PHPUserIniParser = PHPUserIniParser::getInstance($this->sampleExistingUserIni);
        $this->assertEquals(null, $PHPUserIniParser->getProperty("foobar"));
    }

    public function testGetPropertyEmptyWhenFileNotExists()
    {
        $PHPUserIniParser = PHPUserIniParser::getInstance($this->sampleNotExistingUserIni);
        $this->assertEquals(null, $PHPUserIniParser->getProperty("foo"));
    }

    public function testGetPropertyExisting()
    {
        $PHPUserIniParser = PHPUserIniParser::getInstance($this->sampleExistingUserIni);
        $this->assertEquals("UTF-8", $PHPUserIniParser->getProperty("default_charset"));
        $this->assertEquals(0, $PHPUserIniParser->getProperty("define_syslog_variables"));
    }

    public function testSetPropertyEmpty()
    {
        $newValue = "newValue";
        $PHPUserIniParser = PHPUserIniParser::getInstance($this->sampleNotExistingUserIni);
        $PHPUserIniParser->setProperty("foo",$newValue);
        $this->assertEquals($newValue, $PHPUserIniParser->getProperty("foo"));
        $PHPUserIniParser->setProperty("bar",3);
        $this->assertEquals(3, $PHPUserIniParser->getProperty("bar"));
    }

    public function testSetPropertyExisting()
    {
        $newValue = "newValue";
        $PHPUserIniParser = PHPUserIniParser::getInstance($this->sampleExistingUserIni);
        $PHPUserIniParser->setProperty("foo",$newValue);
        $this->assertEquals($newValue, $PHPUserIniParser->getProperty("foo"));
        $PHPUserIniParser->setProperty("bar",3);
        $this->assertEquals(3, $PHPUserIniParser->getProperty("bar"));
        $PHPUserIniParser->setProperty("define_syslog_variables",1);
        $this->assertEquals(1, $PHPUserIniParser->getProperty("define_syslog_variables"));
    }

    public function testRemovePropertyExisting()
    {
        $PHPUserIniParser = PHPUserIniParser::getInstance($this->sampleExistingUserIni);
        $PHPUserIniParser->removeProperty("foo");
        $this->assertEquals(null, $PHPUserIniParser->getProperty("foo"));
    }



    public function tearDown()
    {
        if(file_exists($this->sampleExistingUserIni))
            unlink($this->sampleExistingUserIni);
        if(file_exists($this->sampleNotExistingUserIni))
            unlink($this->sampleNotExistingUserIni);
    }
}