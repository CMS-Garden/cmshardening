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


namespace php\parser;

use L;
use php\core\configuration\Configuration;
use php\vendor\TYPO3\ConfigurationManager;

/**
 * Configuration Parser for Typo3' config file typo3conf/LocalConfiguration.php
 *
 * @package php\parser
 * @author Falk Huber
 */
class Typo3ConfigParser extends ConfigParser {

	private static $instance;

	/**
	 *
	 * @var \php\vendor\TYPO3\ConfigurationManager The ConfigurationManager of Typo3 (copied from TYPO3 7.6.0 sources)
	 */
	private $typo3config;
	
	/**
	 *
	 * @var \php\core\configuration\Configuration The Logger for this class
	 */
	private $logger;

	/**
	 * Creates a Configuration Parser for Typo3's config file typo3conf/LocalConfiguration.php
	 * @param $rootPath	string The path to the root-path of the typo3-installation.
	 * @param $configurationFolder string The path to the configuration-folder of the typo3-installation.
	 */
	protected function __construct($rootPath, $configurationFolder) {
		$this->logger = Configuration::getInstance ()->getLogger ();
		// The TYPO3 ConfigurationManager need certain constants to be set:
		if (! defined ( 'PATH_site' ))
			define ( 'PATH_site', $rootPath );
		if (! defined ( 'PATH_typo3conf' ))
			define ( 'PATH_typo3conf', $configurationFolder );
		if (! defined ( 'TYPO3_OS' ))
			define ( 'TYPO3_OS', "WIN" ); // This is necessary, because other values would cause problems in GeneralUtility->fixPermissions()
		if (! defined ( 'LF' ))
			define ( 'LF', chr ( 10 ) );
		
		$this->sanityCheck (); // test if the above constants are pointing to a proper TYPO3 installation
		$this->typo3config = new ConfigurationManager ();
	}

	public static function getInstance()
	{
		if (!isset(self::$instance))
		{
			self::$instance = new Typo3ConfigParser(
				Configuration::getInstance ()->getProperty ( "typo3.Options.RootPath" ),
				Configuration::getInstance ()->getProperty ( "typo3.Options.ConfigurationFolder" )
			);
		}
		return self::$instance;
	}

	/**
	 *
	 * Returns the value of a give TYPO3 path. The path has to be in form of e.g. "DB/username" or HTTP/proxy_host
	 *
	 * @param string $key
	 *        	The path of the property to retrieve (e.g. DB/username)
	 * @return string|null The value of the found property. If not found null is returned.
	 */
	public function getProperty($key) {
		try {
			$val = $this->typo3config->getLocalConfigurationValueByPath ( $key );
		} catch ( \RuntimeException $e ) {
			$this->logger->warn ( L::Parser_PropertyNotFound ( $key ) );
			return null;
		}
		return $val;
	}
	
	/**
	 * Sets a properties value in the corresponding Configuration file.
	 * If the property is not yet existing, it will be created
	 *
	 * @param string $key
	 *        	The path of the property to retrieve (e.g. DB/username)
	 * @param string $value
	 *        	The value to be set for the property
	 */
	public function setProperty($key, $value) {
		$this->typo3config->setLocalConfigurationValueByPath ( $key, $value );
	}
	
	/**
	 *
	 * Returns the value of a give TYPO3 path. The path has to be in form of e.g. "DB/username" or HTTP/proxy_host
	 *
	 * @param string $key
	 *        	The path of the property to retrieve (e.g. DB/username)
	 */
	public function removeProperty($key) {
		try {
			$this->typo3config->removeLocalConfigurationKeysByPath ( array (
					$key 
			) );
		} catch ( \RuntimeException $e ) {
			$this->logger->warn ( L::Parser_PropertyNotFound ( $key ) );
		}
	}
	/**
	 * Tests if the Constants PATH_site and PATH_typo3conf are pointing to a proper TYPO3 installation
	 * @throws \Exception
	 */
	private function sanityCheck() {
		if (! file_exists ( PATH_site ))
			throw new \Exception ( "Path not found. Please check Config \"Typo3Path\"" );
		if (! file_exists ( PATH_typo3conf ))
			throw new \Exception ( "Path not found. Please check Config \"Typo3ConfigPath\"" );
		if (! file_exists ( PATH_typo3conf . "LocalConfiguration.php" ))
			throw new \Exception ( "File LocalConfiguration.php not found. Please check Config \"Typo3ConfigPath\"" );
	}
}
