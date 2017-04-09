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


namespace php\core\configuration;

use Exception;
use \L;
use \php\core\Logger;
use \php\core\Util;
use \php\io\CLIWriter;

// Load the SPYC library for parsing YAML documents
require_once VENDOR_PATH . 'spyc/spyc.php';

/**
 * This class aims to provide a central configuration for all kinds of overall settings.
 * Here you can fetch information for logging, paths to the webservers documentRoot and other stuff configured in the global YAML file.
 *
 * @author Falk Huber
 *
 */
class Configuration
{

    private static $instance = null;
    /**
     *
     * @var \php\core\Logger The object to log events in the script
     */
    private $logger;

    /**
     * @var \php\io\Writer    The object to print output and prompts for inputs
     */
    private $writer;

    /**
     * @var ConfigurationParser The instance of a ConfigurationParser
     */
    private $parser;

    private function __construct()
    {
        $this->parser = new ConfigurationParser(ROOT_PATH . 'config.yml');
    }

    /**
     * Creates an instance of the Configuration class (Singleton pattern)
     *
     * @return \php\core\configuration\Configuration
     */
    static public function getInstance()
    {
        if (null === self::$instance) {
            self::$instance = new Configuration();
        }
        return self::$instance;
    }

    /**
     * Sets a configuration value to the given property during runtime.
     * The initial Configuration is read from the YAML file, while it is dynamic during the runtime. There is no persistence back to this file.
     *
     * @param string $key
     * @param mixed $value
     * @throws Exception If the property cannot be set because of the current structure of the properties
     */
    public function setProperty($key, $value)
    {
        $this->parser->setProperty($key, $value);
    }

    /**
     * Returns whether the dry-run is activated.
     * @return bool true, when dry-run is activated or not specified, otherwise false.
     */
    public function isDryRun()
    {
        $isDryRun = $this->parser->getProperty("HardeningSettings.CheckOnly");
        if (!empty($isDryRun))
        {
            // Parse "true" or "false".
            $isDryRun = filter_var(str_replace('"', '', $isDryRun), FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            if ($isDryRun === null) {
                // Not a valid parameter. Do DryRun.
                return true;
            }
            return $isDryRun;
        } else {
            return true;
        }
    }

    /**
     * Returns the property matching the supplied key.
     *
     * This method might require user-interaction when following conditions are met:
     * - the property is empty.
     * - the property is not of the type defined in the key's type-property.
     *
     * @param $key string the key of the property to retrieve.
     * @return mixed the property of any type.
     */
    public function &getProperty($key)
    {
        $value = $this->parser->getProperty($key);
        // if the fetched property has no value at all (does not exist or is empty) prompt the user to enter the missing value
        if (Util::is_null_or_empty($value)) {
            $description_label = "";
            $type = "";
            // if the key to fetch already ends with .value
            if (Util::after_last('.', $key) === "value") {
                // We might also trigger an exception here, since accessing properties this way should be prohibited.
                $description_key = preg_replace("value$", "description", $key);
                $description_label = $this->parser->getProperty($description_key);
                $type_key = preg_replace("value$", "type", $key);
                $type = $this->parser->getProperty($type_key);
            }
            $value = $this->promptUserInput($key, $description_label, $type);
            $this->parser->setProperty($key, $value);
        } else if (is_array($value))  // if the fetched property is actually not a scalar but an array
        {
            // if the fetched array contains an item called "value"
            if (isset($value['value'])) {
                $description_label = "";
                if (isset($value["description"]) && !is_null($value["description"]) && !empty($value["description"])) {
                    $description_label = $value["description"];
                }
                $type = "";
                if (isset($value["type"]) && !is_null($value["type"]) && !empty($value["type"])) {
                    $type = $value["type"];
                }
                $default = "";
                if (isset($value["default"]) && !is_null($value["default"]) && !empty($value["default"])) {
                    $default = $value["default"];
                }

                // If this value is null prompt the user to enter the missing value
                if (Util::is_null_or_empty($value["value"])) {
                    $value = $this->promptUserInput($key, $description_label, $type, $default);
                    $this->parser->setProperty($key . ".value", $value);
                } else {
                    // When value not empty and type is set, we do type-checking
                    if (!Util::is_null_or_empty($type) && !TypeChecker::create($type)->check($value["value"])) {
                        $value = $this->promptUserInput($key, $description_label, $type);
                        $this->parser->setProperty($key . ".value", $value);
                    } else {
                        $value = $value["value"];
                    }
                }
            }
            // if the fetched array does not contain a "value" item the whole array is returned e.g. for Hardening.IncludeModules
        }
        return $value;
    }

    /**
     * Checks whether the property is null or empty.
     * @param $key string the key of the property. Usually a namespace.
     * @return bool true, when property exists, otherwise false.
     */
    public function doesPropertyExist($key)
    {
        return !Util::is_null_or_empty($this->parser->getProperty($key));
    }


    private function promptUserInput($key, $description_label, $type = "", $default = "")
    {
        $this->getWriter()->write(L::Dialog_missingProperty($key));
        $this->getLogger()->info(L::Dialog_missingProperty($key));
        $description = Util::resolveTranslationLabel($description_label);
        if (!empty($description))
            $this->getWriter()->write($description);

        $value = $this->getWriter()->promptUserInput(L::Dialog_missingPropertyPrompt($key), $type, $default);
        $this->getLogger()->info(L::Dialog_UserEntered(var_export($value,true)));
        return $value;
    }

    /**
     * For each $name a new Log file is created and returned in form of a Logger object
     *
     * @return \php\core\Logger
     */
    public function getLogger()
    {
        if ($this->logger)
            return $this->logger;
        $this->logger = new Logger ();
        return $this->logger;
    }

    /**
     * Returns a proper output Writer depending on the method the php script is called
     * @return \php\io\Writer
     * @throws \Exception   If there is no Writer implementation could be found
     */
    public function getWriter()
    {
        if ($this->writer)
            return $this->writer;
        if (Util::isCLI()) {
            return $this->writer = new CLIWriter();
        }
        throw new \Exception(L::Global_NotCLI);
    }

    public static function handleSig($signal)
    {
        ConfigurationParser::handleSig($signal);
    }

}