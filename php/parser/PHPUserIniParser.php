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

/**
 * Class PHPUserIniParser
 * getProperty will only read the .htaccess file and not anything from a php.ini file or from ini_get() as this script might run in a different PHP environment as the CMS
 * @package php\parser
 */
class PHPUserIniParser extends ConfigParser
{
    public $userIniFilePath;
    protected $userIniContent = array();
    protected static $instance = null;

    /**
     * PHPUserIniParser constructor.
     * @param $userIniFilePath string the path to the local .user.ini file (consider the php directive user_ini.filename
     */
    private function __construct($userIniFilePath)
    {
        $this->userIniFilePath = $userIniFilePath;
        if (file_exists($this->userIniFilePath)) {
            $this->userIniContent = parse_ini_file($this->userIniFilePath, true, INI_SCANNER_RAW);
        } else {
            $this->userIniContent = array();
        }
        // .user.ini file will be created later (setProperty) when it does not exist.
        if (!file_exists($this->userIniFilePath)) {
            Configuration::getInstance()->getLogger()->info(L::Parser_FileCreatedByScript($userIniFilePath));
            Configuration::getInstance()->getWriter()->write(L::PHP_FileNewlyCreated($userIniFilePath));
            Configuration::getInstance()->getWriter()->write("");
        }

    }

    public static function getInstance($userIniFilePath)
    {
        if (!isset(self::$instance) || self::$instance->userIniFilePath !== $userIniFilePath) {
            self::$instance = new PHPUserIniParser($userIniFilePath);
        }
        return self::$instance;
    }

    /**
     * getProperty will only read the .htaccess file and not anything from a php.ini file or from ini_get() as this script might run in a different PHP environment as the CMS
     * @inheritdoc
     */
    public function getProperty($key)
    {
        if (!array_key_exists($key, $this->userIniContent))
            return null;
        return $this->parseValue($this->userIniContent[$key]);
    }

    /**
     * @inheritdoc
     */
    public function setProperty($key, $value)
    {
        $this->userIniContent[$key] = $value;
        $this->write_php_ini($this->userIniContent, $this->userIniFilePath);
    }

    /**
     * @inheritdoc
     */
    public function removeProperty($key)
    {
        unset($this->userIniContent[$key]);
        $this->write_php_ini($this->userIniContent, $this->userIniFilePath);
    }

    /**
     * Parses an Array to write it back as an ini file
     * @param $array array The array with the ini options
     * @param $file string the path of the ini file to be written
     */
    private function write_php_ini($array, $file)
    {
        $res = array();
        foreach ($array as $key => $val) {
            if (is_array($val)) {
                $res[] = "[$key]";
                foreach ($val as $skey => $sval) $res[] = "$skey = " . (is_numeric($sval) ? $sval : '"' . $sval . '"');
            } else $res[] = "$key = " . (is_numeric($val) ? $val : '"' . $val . '"');
        }
        $this->safefilerewrite($file, implode("\r\n", $res));
    }


    /**
     * Safely overwrite a file
     * @param $fileName
     * @param $dataToSave
     */
    private function safefilerewrite($fileName, $dataToSave)
    {
        if ($fp = fopen($fileName, 'w')) {
            $startTime = microtime(TRUE);
            do {
                $canWrite = flock($fp, LOCK_EX);
                // If lock not obtained sleep for 0 - 100 milliseconds, to avoid collision and CPU load
                if (!$canWrite) usleep(round(rand(0, 100) * 1000));
            } while ((!$canWrite) and ((microtime(TRUE) - $startTime) < 5));

            //file was locked so now we can store information
            if ($canWrite) {
                fwrite($fp, $dataToSave);
                flock($fp, LOCK_UN);
            }
            fclose($fp);
            chmod($this->userIniFilePath, 0644);
        } else {
            Configuration::getInstance()->getLogger()->error("Writing " . $fileName . " failed!");
        }
    }


}