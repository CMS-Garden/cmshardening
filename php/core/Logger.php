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

use Exception;
use \php\core\configuration\Configuration;
use \php\core\Util;

define("LOGFILENAMEPATTERN", "log_{date}.log");

/**
 * Simple file logger
 *
 * @author Falk Huber *
 */
class Logger
{
    private $location;
    private $fileHandler;

    /**
     * A file is created or opened (if already existing) to add new log messages.
     * The location of the logs is configured in the configuration property "LogLocation".
     *
     * @throws Exception
     */
    public function __construct()
    {
        $this->location = ROOT_PATH . Configuration::getInstance()->getProperty("Logging.LogLocation");
        if (!file_exists($this->location))
            mkdir($this->location, 0777, true);
        $this->filepath = $this->location . DIRECTORY_SEPARATOR . str_replace("{date}", Util::nowForFiles(), LOGFILENAMEPATTERN);
        $this->fileHandler = fopen($this->filepath, 'a') or die ("can't open log file" . $this->filepath);
    }

    public function __destruct()
    {
        if (is_resource($this->fileHandler))
            fclose($this->fileHandler);
    }

    public function info($s)
    {
        $this->writeLog("INFO", $s);
    }

    public function debug($s)
    {
        $this->writeLog("DEBUG", $s);
    }

    public function warn($s)
    {
        $this->writeLog("WARN", $s);
    }

    public function error($s)
    {
        $this->writeLog("ERROR", $s);
    }

    public function trace($s)
    {
        $this->writeLog("TRACE", $s);
    }

    /**
     * Writes a new message to the log file
     *
     * @param string $severity
     *            The severity of the log entry
     * @param string $string
     *            The actual message to be logged
     * @throws Exception if the file handler is not valid
     */
    private function writeLog($severity, $string)
    {
        $str = "[" . Util::nowForLogs() . "]\t[$severity]\t" . "\t[" . $this->getCallerClass() . "]\t" . $string;
        if (is_resource($this->fileHandler))
            fwrite($this->fileHandler, $this->str_format($str) . PHP_EOL);
    }

    private function getCallerClass()
    {
        list(, , $caller) = debug_backtrace(false, 3);
        if (!$caller || !array_key_exists("file", $caller))
            return "";
        $filename = basename($caller["file"]);
        return str_replace(".php", "", $filename);
    }

    /**
     * Formats special characters within a string.
     *
     * Following table lists the special-characters and their mapping:
     *
     * Special-Character | Mapping
     *      ${n}$        | \n
     *      ${t}$        | \t
     *
     * @param $text string containing special-characters.
     * @return string the formatted text.
     */
    private function str_format($text)
    {
        $text = str_replace('§{n}', PHP_EOL, $text);
        $text = str_replace('§{t}', "\t", $text);
        return $text;
    }
}