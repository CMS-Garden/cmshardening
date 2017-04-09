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
use php\parser\HtAccessParser;
use PHPUnit_Framework_TestCase;

class HtAccessParserTest extends PHPUnit_Framework_TestCase
{
    private $sampleNotExistingHtAccess = TEST_PATH . 'samples/PHPhtaccess/.htaccess_notexisting';
    private $sampleExistingHtAccess = TEST_PATH . 'samples/PHPhtaccess/.htaccess_existing';

    public function setUp()
    {
        // recover the existing .htaccess from the backup-file
        copy($this->sampleExistingHtAccess . '_backup', $this->sampleExistingHtAccess);

    }

    public function testGetPropertyEmpty()
    {
        $HtAccessParser = HtAccessParser::getInstance($this->sampleNotExistingHtAccess);
        $this->assertEquals(null, $HtAccessParser->getProperty("foo"));
    }

    public function testGetPropertyExisting()
    {
        $HtAccessParser = HtAccessParser::getInstance($this->sampleExistingHtAccess);
        $this->assertEquals(".:/usr/local/lib/php", $HtAccessParser->getProperty("include_path"));
        $this->assertEquals("on", $HtAccessParser->getProperty("engine"));
        $this->assertEquals(null, $HtAccessParser->getProperty("foo"));
    }

    public function testSetPropertyEmpty()
    {
        $HtAccessParser = HtAccessParser::getInstance($this->sampleNotExistingHtAccess);
        // Testing Values
        $newValue = "newValue";
        $HtAccessParser->setProperty("foo",$newValue);
        $this->assertEquals($newValue, $HtAccessParser->getProperty("foo"));

        $HtAccessParser->setProperty("bar",3);
        $this->assertEquals(3, $HtAccessParser->getProperty("bar"));

        // Testing Flags
        $HtAccessParser->setProperty("lorem","off");
        $this->assertEquals("off", $HtAccessParser->getProperty("lorem"));

        $HtAccessParser->setProperty("ipsum","ON");
        $this->assertEquals("on", $HtAccessParser->getProperty("ipsum"));

    }

    public function testSetPropertyExisting()
    {
        $newValue = "newValue";
        $HtAccessParser = HtAccessParser::getInstance($this->sampleExistingHtAccess);
        $HtAccessParser->setProperty("foo",$newValue);
        $this->assertEquals($newValue, $HtAccessParser->getProperty("foo"));
        $HtAccessParser->setProperty("bar",3);
        $this->assertEquals(3, $HtAccessParser->getProperty("bar"));
        $HtAccessParser->setProperty("define_syslog_variables",1);
        $this->assertEquals(1, $HtAccessParser->getProperty("define_syslog_variables"));
    }

    public function testRemovePropertyExisting()
    {
        $HtAccessParser = HtAccessParser::getInstance($this->sampleExistingHtAccess);
        $HtAccessParser->removeProperty("foo");
        $this->assertEquals(null, $HtAccessParser->getProperty("foo"));
    }



    public function tearDown()
    {
        if(file_exists($this->sampleExistingHtAccess))
            unlink($this->sampleExistingHtAccess);
        if(file_exists($this->sampleNotExistingHtAccess))
            unlink($this->sampleNotExistingHtAccess);
    }
}