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
use php\core\storage\TransactionManager;
use \L;

/**
 * Class ConfigurationParser
 * This class's purpose is to parse the yaml configuration files and provide access to this configuration.
 * @package php\core\configuration
 */
class ConfigurationParser
{
    private $configFileLocation;

    /**
     *
     * @var array $properties Holds all the configuration as an array tree. Access these properties via getProperty($key)
     */
    private $properties;

    /**
     * Constructor
     * Loads the global Configuration File config.yml and tries to load all the necessary additional YAML files within the modules-directory as stated in Hardening.IncludePackages.
     * @param $configFileLocation string the location of the config file (usually config.yml)
     * @throws Exception if the configuration file cannot be found or opened
     */
    public function __construct($configFileLocation)
    {
        $this->loggerMap = array();
        if (!file_exists($configFileLocation))
            throw new Exception ("Configuration File not found: " . $this->configFileLocation);

        $this->configFileLocation = $configFileLocation;
        $this->properties = \Spyc::YAMLLoad($this->configFileLocation);
        $configFileContent = file_get_contents($this->configFileLocation);
        if (strpos($configFileContent, "\t") !== false) {
            throw new Exception ("The yml-file does contain invalid characters (tabs) which often lead to parser-issues. Please replace them by spaces to continue.");
        }

        // Include all yaml configs for the hardening packages
        $packages = $this->getProperty("Hardening.IncludeModules");
        foreach ($packages as $package) {
            $fileToInclude = MODULES_PATH . $package . ".yml";
            if (file_exists($fileToInclude)) {
                $configFileContent = $this->merge_config_file($package, $fileToInclude, $configFileContent);
            } else {
                echo "Could not load module configuration $fileToInclude ($package is configured in ".$this->configFileLocation." Hardening.IncludeModules.".PHP_EOL;
            }
        }

        // Reloads the config-file including all merged contents to support anchors.
        $this->properties = \Spyc::YAMLLoadString($configFileContent);
    }

    /**
     * Returns a value to a given property.
     * The initial Configuration is read from the YAML file, while it is dynamic during the runtime.
     * If the key doesn't point to a node (not leaf) in the yaml tree an array is returned
     *
     * @param string $key
     * @return mixed Returns the value of the yaml tree or null if there is no property found
     */
    public function &getProperty($key)
    {
        // split key into parts separated by .
        $parts = explode('.', $key);
        // try to travers the yaml tree based on the parts. The currentnode will point to the current position in the tree
        $currentnode =& $this->properties;
        $null = null;
        foreach ($parts as $part) {

            if (!is_array($currentnode) || !array_key_exists($part, $currentnode))
                return $null;
            $currentnode =& $currentnode [$part];
            if (is_null($currentnode))
                return $null;
        }
        return $currentnode;
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
        /*
         * If there is no node for this key in the yaml tree, try to find the most deepest node for this key (e.g. node1.node13 for node1.node13.node135)
         */
        $QueriedParts = explode(".", $key);
        $unresolvedParts = array();
        do {
            $property =& $this->getProperty(implode(".", $QueriedParts));
            if (!is_null($property))
                break;
            array_unshift($unresolvedParts, array_pop($QueriedParts));
        } while (!empty($QueriedParts));
        // if there is no path in the yaml tree at all select the the whole properties tree as $property
        if (empty($property)) $property = $this->properties;
        /*
         * If there is no node for the key the tree will be extended to create a proper node
         */
        foreach ($unresolvedParts as $unresolvedPart) {
            if (gettype($property) == "array") {
                $property[$unresolvedPart] = array();
                $property =& $property[$unresolvedPart];
            } else {
                throw new Exception("Cannot set Configuration $key as the path in the tree is already containing an atomic value, which cannot be extended.");
            }
        }
        $property = $value;
    }

    /**
     * Merges an YAML file to the config-file-content and returns it as string.
     * @param $package string the package which is used as identifier within the merged config-file.
     * @param $fileToInclude string the file which should be merged with the config file.
     * @param $configFileContent string the content of the yaml file to merge.
     * @return string the merged config-file as string.
     */
    private function merge_config_file($package, $fileToInclude, $configFileContent)
    {
        // attaches package name in front and indents the content of the additional yaml file content
        return $configFileContent . "\n" . "$package:\n  " . implode("\n  ", explode("\n", file_get_contents($fileToInclude)));
    }

    public static function handleSig($signal)
    {
        Configuration::getInstance()->getWriter()->writeError(L::Dialog_KillScript);
        Configuration::getInstance()->getLogger()->error(L::Dialog_KillScript);
        TransactionManager::getInstance()->rollBackAllTransactions();
        exit("");
    }

    /**
     * @deprecated this method is only used for debugging.
     * @return array returns all properties of the loaded configuration-file as array.
     */
    public function getPropertiesAsArray()
    {
        return \Spyc::YAMLDump($this->properties);
    }
}