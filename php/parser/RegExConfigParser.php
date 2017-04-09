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
use \php\core\Util;

/**
 * Class RegExConfigParser
 * Configuration Parser for configuration file based on a regular expression
 *
 * @package php\parser
 * @author Falk Huber
 * @see WordpressConfigParser, JoomlaConfigParser
 */
abstract class RegExConfigParser extends ConfigParser
{
    /**
     *
     * @var String The full path to the configuration file
     */
    protected $configFile;
    /**
     *
     * @var String The content of the configuration file
     */
    protected $configContent;
    /**
     *
     * @var \php\core\Logger the local logger object
     */
    protected $logger;
    /**
     *
     * @var string The regular expression to search for a property
     */
    protected $regexPattern;
    /**
     *
     * @var string A string that is used to add a new property. Use the placeholder %%key%% and %%value%%
     * @example define('%%key%%', %%value%%);
     */
    protected $addPropertySchema;
    /**
     *
     * @var string The usual Ending string of a configuration file e.g. "}" or "?>"
     */
    protected $fileEnding;

    protected $commentCharacters = "//";

    protected $formatValue2String = true;

    /**
     * Destructor that persists any changes, by writing out the Configuration back to the wp-config.php
     */
    public function __destruct()
    {
        $this->persistChanges();
    }

    /**
     *
     * {@inheritDoc}
     *
     * @see IConfigParser::getProperty()
     */
    public function getProperty($key)
    {
        $propertyMatches = $this->findPropertyMatches($key);
        switch (sizeof($propertyMatches)) {
            case 0 :
                return null;
            case 1 :
                return $this->parseValue($propertyMatches [0]);
            default :
                $this->logger->warn(L::Parser_MultipleEntries($key, $this->configFile));
                return $this->parseValue(array_pop($propertyMatches));
        }
    }

    /**
     *
     * {@inheritDoc}
     *
     * @see IConfigParser::setProperty()
     */
    public function setProperty($key, $value)
    {
        if($this->formatValue2String)
            $value = $this->escapeValue($value);
        $propertyMatches = $this->findPropertyMatches($key);
        $wholePropertyMatches = $this->findPropertyMatches($key, true);
        switch (sizeof($propertyMatches)) {
            case 0 :
                // if there is no property of this name a new property is written to the end of the file
                $this->addPropertyToFileEnd($key, $value);
                break;
            case 1 :
                // If there is already one existing property, this one will be replaced
                foreach ($wholePropertyMatches as $match) {
                    $oldProperty = $propertyMatches [0];
                    $match = str_replace("\n", "", $match);
                    $replace = $this->commentCharacters . " " . L::Parser_PropertyChanged(Util::now()) . PHP_EOL .
                        str_replace($oldProperty, $value, $match);
                    $this->configContent = str_replace($match, $replace, $this->configContent);
                }
                break;
            default :
                // If there are multiple properties of this name, all of these are commented and a new one is written to the end of the file
                foreach ($wholePropertyMatches as $match) {
                    $match = str_replace("\n", "", $match);
                    $replace = $this->commentCharacters . " " . L::Parser_PropertyRemoved(Util::now()) . PHP_EOL .
                        $this->commentCharacters . " " . $match;
                    $this->configContent = str_replace($match, $replace, $this->configContent);
                }
                $this->addPropertyToFileEnd($key, $value);
        }
        $this->persistChanges();
    }

    /**
     *
     * {@inheritDoc}
     *
     * @see IConfigParser::removeProperty()
     */
    public function removeProperty($key)
    {
        $wholePropertyMatches = $this->findPropertyMatches($key, true);
        foreach ($wholePropertyMatches as $match) {
            $match = str_replace("\n", "", $match);
            $replace = $this->commentCharacters . " " . L::Parser_PropertyRemoved(Util::now()) . PHP_EOL .
                "// " . $match;
            $this->configContent = str_replace($match, $replace, $this->configContent);
        }
        $this->persistChanges();
    }

    /**
     * Persists any changes, by writing out the Configuration back to the wp-config.php
     */
    public function persistChanges()
    {
        if (!file_put_contents($this->configFile, $this->configContent)) {
            $handle = fopen($this->configFile, "w");
            fwrite($handle, $this->configContent);
            fclose($handle);
        }

    }

    /**
     * Finds all values to a given property key in the configuration file
     *
     * @param string $key
     *            The Property to find in the configuration
     * @param boolean $getWholeMatch
     *            If true, the return would be the whole match of the regex ("\ndefine(...);")
     * @return array An array of the found values for the property $key
     */
    protected function findPropertyMatches($key, $getWholeMatch = false)
    {
        // quoted Key for regex
        $qkey = preg_quote($key, "/");
        $matches = array();
        $pattern = str_replace('%%key%%', $qkey, $this->regexPattern);
        preg_match_all($pattern, $this->configContent, $matches);

        if ($matches && sizeof($matches) == 2 && is_array($matches [1]))
            if ($getWholeMatch)
                return $matches [0];
            else {
                return $matches [1];
            }
        return array();
    }

    /**
     * Writes a new property at the end of the file
     *
     * @param string $key
     *            The key of the property
     * @param string $value
     *            The value of the property
     */
    protected function addPropertyToFileEnd($key, $value)
    {
        // remove the trailing } of the file (and afterwards add it again
        $this->configContent = rtrim($this->configContent, $this->fileEnding . "\t\r\n");
        $propertySchema = str_replace("%%key%%", $key, $this->addPropertySchema);
        $propertySchema = str_replace("%%value%%", $value, $propertySchema);
        $this->configContent .= PHP_EOL . $this->commentCharacters . " " . L::Parser_PropertyAdded(Util::now()) . PHP_EOL .
            $propertySchema .
            PHP_EOL . $this->fileEnding;
    }

    /**
     * This method sets the configuration file to be parsed and loads the content of the configuration file in a local variable
     * @param $configFile   string The absolute path to the configuration file
     * @throws \Exception   in case the file cannot be loaded
     */
    protected function setConfigFile($configFile)
    {
        $this->configFile = $configFile;
        $this->loadConfigFile();


    }

    /**
     * Returns the configuration file to be parsed
     * @return String
     */
    public function getConfigFile()
    {
        return $this->configFile;
    }

    /**
     * Sets the logger from the extending classes to not use RegExConfigParser as name for the logger but the more exact one.
     * @param $logger  \php\core\Logger
     * @return $this
     */
    protected function setLogger($logger)
    {
        $this->logger = $logger;
        return $this;
    }

    /**
     * Defines the regular expression to be used when parsing the configuration file for a property.
     * The regular expression has to start with a newline (\n) and has to mark the spot where the value is found with brackets. The quotes (",') of the value have to be included here.
     * @param $regexPattern string The regular expression
     */
    protected function setRegexPattern($regexPattern)
    {
        $this->regexPattern = $regexPattern;
    }

    /**
     * Sets a string that is used to add a new property.
     * Use the placeholder %%key%% and %%value%%
     *
     * @example define('%%key%%', %%value%%);
     * @param string $addPropertySchema
     *            The schema to set
     */
    protected function setAddPropertySchema($addPropertySchema)
    {
        $this->addPropertySchema = $addPropertySchema;
    }

    /**
     *
     * @param string $fileEnding
     *            the Ending of the file, that occurs after all configuration, e.g. } or ?>
     */
    protected function setFileEnding($fileEnding)
    {
        $this->fileEnding = $fileEnding;
    }

    /**
     * Sets the Comment Character. Default is "//". You can change it to e.g. "#"
     * @param string $commentCharacters
     */
    public function setCommentCharacters($commentCharacters)
    {
        $this->commentCharacters = $commentCharacters;
    }

    /**
     * @param boolean $formatValue2String
     */
    public function setFormatValue2String($formatValue2String)
    {
        $this->formatValue2String = $formatValue2String;
    }



    public function loadConfigFile()
    {
        // Trying to read the file's content
        if (!file_exists($this->configFile))
            throw new \Exception ("File not found: " . $this->configFile);
        // in case some functions are disabled by disable_function
        switch (true) {
            case function_exists('file_get_contents') :
                $this->configContent = file_get_contents($this->configFile);
                if (!empty($this->configFile))
                    break;
            case (function_exists('fopen') && function_exists('fread') && function_exists('filesize')) :    //TODO: Never really tested this case
                $handle = fopen($this->configFile, "r");
                $this->configContent = fread($handle, filesize($this->configFile));
                fclose($handle);
                break;
            // TODO: some other cases if the above functions are disabled by php (disable_functions)
        }
        // for .htaccess files it may happen that the file is empty
        //if (empty ($this->configContent))
        //    throw new \Exception ("No Content found in " . $this->configFile);
    }
}