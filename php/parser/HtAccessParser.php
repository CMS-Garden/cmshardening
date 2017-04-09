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


use php\core\configuration\Configuration;
use \L;
use \Exception;


/**
 * Class HtAccessParser
 * getProperty will only read the .htaccess file and not anything from a php.ini file or from ini_get() as this script might run in a different PHP environment as the CMS
 * @package php\parser
 */
class HtAccessParser extends RegExConfigParser
{
    protected static $instance = null;

    private static $FLAG = 0;
    private static $VALUE = 1;
    private static $regExPatternPhpValue = '/\n\s*php_value ' . '%%key%%' . '\s+([\'|"]?.*[\'|"]?)/';
    private static $regExPatternPhpFlag = '/\n\s*php_flag ' . '%%key%%' . '\s+([\'|"]?.*[\'|"]?)/';
    private static $regExAddPropertySchemaPhpValue = 'php_value %%key%% %%value%%';
    private static $regExAddPropertySchemaPhpFlag = 'php_flag %%key%% %%value%%';
    // TODO: Check if php_admin_value and php_admin_flag can be used instead to increase security, ref: http://www.php.net/php_value


    /**
     * Creates a Configuration Parser for a .htaccess file
     * @param $configFile string the path to the .htaccess file
     * @throws Exception if the file is not readable
     */
    protected function __construct($configFile)
    {
        $this->setLogger(Configuration::getInstance()->getLogger());
        // create .htaccess file if it does not exist
        if (!file_exists($configFile)) {
            $this->logger->info(L::Parser_FileCreatedByScript($configFile));
            Configuration::getInstance()->getWriter()->write(L::PHP_FileNewlyCreated($configFile));
            $fh = fopen($configFile, 'w');
            fclose($fh);
            chmod($configFile, 0644);
        }

        $this->setConfigFile($configFile);
        // .htaccess uses different Comment characters (#) compared to the RegExConfigParser (//)
        $this->setCommentCharacters("#");
    }

    /**
     * {@inheritDoc}
     * @see IConfigParser::getProperty()
     */
    public function getProperty($key)
    {
        $this->switchValueFlag(HtAccessParser::$VALUE);
        $ret = parent::getProperty($key);
        if ($ret === null) {
            $this->switchValueFlag(HtAccessParser::$FLAG);
            $ret = parent::getProperty($key);
        }
        return $ret;
    }

    /**
     * {@inheritDoc}
     * @see IConfigParser::setProperty()
     */
    public function setProperty($key, $value)
    {
        if (strtolower($value) === "on" || strtolower($value) === "off") {
            $this->switchValueFlag(HtAccessParser::$FLAG);
            parent::setProperty($key, strtolower($value));
        } else {
            $this->switchValueFlag(HtAccessParser::$VALUE);
            parent::setProperty($key, $value);
        }
    }

    /**
     * {@inheritDoc}
     * @see IConfigParser::removeProperty()
     */
    public function removeProperty($key)
    {
        $this->switchValueFlag(HtAccessParser::$FLAG);
        parent::removeProperty($key);
        $this->switchValueFlag(HtAccessParser::$VALUE);
        parent::removeProperty($key);
    }

    public static function getInstance($configFile)
    {
        if (!isset(self::$instance) || self::$instance->getConfigFile() !== $configFile) {
            self::$instance = new HtAccessParser($configFile);
        }
        return self::$instance;
    }

    /**
     * There are two ways of setting php configs in .htaccess: php_value and php_flag. Last one is for on|off values. To configure the RegExConfigParser properly for both ways this switch function is a helper
     * @param $type int the
     * @throws Exception if the given type is not valid
     */
    private function switchValueFlag($type)
    {
        switch ($type) {
            case HtAccessParser::$FLAG:
                $this->setRegexPattern(HtAccessParser::$regExPatternPhpFlag);
                $this->setAddPropertySchema(HtAccessParser::$regExAddPropertySchemaPhpFlag);
                // the following prevents quotes around the on|off in "php_flag assert.active off"
                $this->setFormatValue2String(false);
                break;
            case HtAccessParser::$VALUE:
                $this->setRegexPattern(HtAccessParser::$regExPatternPhpValue);
                $this->setAddPropertySchema(HtAccessParser::$regExAddPropertySchemaPhpValue);
                $this->setFormatValue2String(true);
                break;
            default: throw new Exception('The given type for switchValueFlag is not valid. Allowed are only HtAccessParser::$FLAG and HtAccessParser::$VALUE');
        }

    }
}