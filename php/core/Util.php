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


namespace php\core;

use php\core\configuration\Configuration;

/**
 * Class Util
 * This class holds small utilities to keep the actual code small and clean
 * @package php\core
 */
class Util
{

    /**
     * Private constructor. This class only contains static methods.
     */
    private function __construct()
    {
    }

    /**
     * Generates the current datetime and format it properly
     * @return String the current datetime in proper format
     */
    public static function now()
    {
        return date(DATE_ATOM);
    }

    /**
     * Generates the current datetime and format it properly to use it in file names
     * @return string the current datetime in proper format
     */
    public static function nowForFiles()
    {
        return date("Y-m-d_H-i-s");
    }

    /**
     * Generates the current date and format it properly to use it in file names
     * @return string the current date in proper format
     */
    public static function currentDate()
    {
        return date("Y-m-d");
    }

    /**
     * Generates the current datetime and format it properly to use it in logs
     * @return string the current datetime in proper format
     */
    public static function nowForLogs()
    {
        return date("Y/m/d H:i:s");
    }

    public static function isCLI()
    {
        return (stripos(php_sapi_name(),'cli')===true || defined('STDIN') || Configuration::getInstance()->getProperty('Dialog.forceCLI') );
    }

    public static function isWindows()
    {
        return strtoupper(substr(PHP_OS, 0, 3)) === 'WIN';
    }

    /**
     * Builds a file path with the appropriate directory separator.
     * @param $segments array unlimited number of path segments
     * @return string Path
     */
    public static function fileBuildPath(...$segments)
    {
        return join(DIRECTORY_SEPARATOR, $segments);
    }

    /**
     * Builds a config path with the appropriate dot separator.
     * @param $segments array unlimited number of path segments
     * @return string Path
     */
    public static function configBuildPath(...$segments)
    {
        return join(".", $segments);
    }

    /**
     * Checks whether the supplied $string is null or an empty string.
     * @param $string string string to check if it is empty or null
     * @return bool true if string is empty or null
     */
    public static function is_null_or_empty($string)
    {
        return is_null($string) || (is_string($string) && strlen($string) === 0);
    }

    /**
     * Checks whether the supplied $string ends with the $test-string.
     * @param $string string the string which should be checked.
     * @param $test string the string which should be contained at the end of $string.
     * @return bool true, when $test is contained at the of $string, otherwise false.
     */
    function endswith($string, $test) {
        $strlen = strlen($string);
        $testlen = strlen($test);
        if ($testlen > $strlen) return false;
        return substr_compare($string, $test, $strlen - $testlen, $testlen) === 0;
    }

    /**
     * Returns the string after of the last occurrence of the string $needle.
     * @param $needle string the string to be searched
     * @param $inthat string the string to search in
     * @return string the string after of the last occurrence of the string $needle.
     */
    public static function after_last($needle, $inthat)
    {
        if (!is_bool(Util::strrevpos($inthat, $needle)))
            return substr($inthat, Util::strrevpos($inthat, $needle) + strlen($needle));
        return "";
    }

    /**
     * Returns the position of the last occurrence of needle within instr or false, when needle was not found.
     * @param $instr string
     * @param $needle string
     * @return bool|int the position of the last occurrence of needle within instr or false, when needle was not found.
     */
    public static function strrevpos($instr, $needle)
    {
        $rev_pos = strpos(strrev($instr), strrev($needle));
        if ($rev_pos === false) return false;
        else return strlen($instr) - $rev_pos - strlen($needle);
    }

    /**
     * Maps translation-label to translation-text.
     * @param $translationLabel string The label of the translation to be resolved
     * @return string empty or the mapped translation-text of the translation-label.
     */
    public static function resolveTranslationLabel($translationLabel)
    {
        if (is_null($translationLabel) || empty($translationLabel)) {
            return "";
        }
        $translation = \L::__callStatic($translationLabel, array());
        if (!is_null($translation) && !empty($translation)) {
            return $translation;
        } else {
            return "";
        }
    }

    /**
     * Returns whether the supplied value is a integer.
     * @param $value mixed the value of any type.
     * @return bool true, when value is an integer, otherwise false.
     */
    public static function is_integer($value)
    {
        return (ctype_digit(strval($value)));
    }

    /**
     * Returns whether the supplied value is a boolean or the string "true"/"false" (case-insensitive).
     * @param $value mixed the value of any type.
     * @return bool true, when value is a boolean or the string "true"/"false" (case-insensitive), otherwise false.
     */
    public static function is_bool($value)
    {
        if (is_bool($value)) {
            return true;
        }
        if (is_string($value)) {
            $value = strtolower($value);
            return ($value === "true" || $value === "false");
        }
        return false;
    }

    /**
     * Returns whether the syntax of the supplied php-file is correct.
     * @param $file mixed the php-file which should be checked.
     * @return bool true, when syntax is ok, otherwise false.
     */
    public static function check_php_syntax($file)
    {
        // Redirect stderr to stdout to suppress displaying errors.
        exec('php -l ' . $file . ' 2>&1', $arrMsgError, $nCodeError);
        return $nCodeError === 0; // No errors.
    }

    /**
     * Checks whether the supplied filename is a directory and ends with a directory-separator.
     * @param $filename mixed the filename which should be checked.
     * @return bool true, when the filename is a directory and ends with a trailing directory-separator, otherwise false.
     */
    public static function is_dir($filename)
    {
        if (is_dir($filename))
        {
            return Util::endswith($filename, DIRECTORY_SEPARATOR);
        }
        return false;
    }

}