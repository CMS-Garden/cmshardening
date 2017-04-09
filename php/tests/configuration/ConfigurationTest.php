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


namespace php\tests\configuration;

require_once 'core/bootstrap.php';
use \php\core\configuration\Configuration;

class ConfigurationTest extends \PHPUnit_Framework_TestCase {
	private $config;
	public function setUp() {
		$this->config = Configuration::getInstance ();
	}
	public function testGetProperty() {
		$this->assertEquals ( "logs/", $this->config->getProperty ( "Logging.LogLocation" ) );
	}

	/*public function testMerge() {
		$this->assertNotEmpty ( $this->config->getProperty ( "wordpress.Options.RootPath" ) );
	}*/

	public function testSetPropertyExisting() {
		$val = rand(0,100);
		$this->config->setProperty("Logging.LogLevel",$val);
		$this->assertEquals($val, $this->config->getProperty("Logging.LogLevel"));
	}
	public function testSetPropertyNotExisting() {
		$val = rand(0,100);
		$this->config->setProperty("Logging.foo.bar.barium",$val);
		$this->assertEquals($val, $this->config->getProperty("Logging.foo.bar.barium"));
	}

	public function testSetPropertyTreeExisting() {
		$this->setExpectedException("Exception");
		$val = rand(0,100);
		$this->config->setProperty("Logging.LogLevel.foo",$val);
	}

	public function tearDown() {
	}
}