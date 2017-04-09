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
use Exception;
use \L;
use php\core\configuration\Configuration;
use php\core\Util;

/**
 * Configuration Parser for Joomla' config file configuration.php
 *
 * @package php\parser
 * @author Falk Huber
 */
class JoomlaConfigParser extends RegExConfigParser {

	protected static $instance = null;

	/**
	 * Creates a Configuration Parser for Joomla's config file configuration.php
	 * @param $configFile string the path to the Joomla config-file.
	 * @throws Exception if the file is not readable
	 */
	protected function __construct($configFile) {
		if (!Util::check_php_syntax($configFile))
		{
			throw new Exception(L::Error_FileNotReadable($configFile));
		}
		$this->setLogger ( Configuration::getInstance ()->getLogger () );
		$this->setConfigFile ( $configFile );
		$this->setRegexPattern ( '/\n\s*public \$' . '%%key%%' . '\s*=\s*([\'|"]?.*[\'|"]?);/' );
		$this->setAddPropertySchema ( "\tpublic $%%key%% = %%value%%;" );
		$this->setFileEnding ( "}" );
	}

	public static function getInstance() {
		if (!isset(self::$instance)) {
			self::$instance = new JoomlaConfigParser(
				Configuration::getInstance ()->getProperty ( "joomla.Options.RootPath" ) .
				Configuration::getInstance ()->getProperty ( "joomla.Options.ConfigurationFile" )
			);
		}
		return self::$instance;
	}

	public static function fromFile($configFile)
	{
		return new JoomlaConfigParser($configFile);
	}

	/**
	 * Returns the property with the specified key.
	 * Starting and ending quotes (') will be removed from the resulting string.
	 * @param string $key the key of the property.
	 * @return string the property with the specified key.
	 */
	public function getProperty($key)
	{
		return trim(parent::getProperty($key), "'");
	}
}