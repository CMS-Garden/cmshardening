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


namespace php\utils\configfile;

use Exception;
use \L;
use php\core\configuration\Configuration;
use php\core\Util;
use php\core\storage\TransactionManager;
use \php\utils\UtilObject;

/**
 * Base-Class to all ConfigurationFileEntries to access the key-value-pair in a more convenient way.
 */
abstract class ConfigFileEntry extends UtilObject
{

    private $key = "";
    private $runIfOptions;
    private $runIfConditionText;

    /**
     * @inheritdoc
     */
    public function __construct($actionParameters, $sectionOptions, $moduleOptions)
    {
        parent::__construct($actionParameters, $sectionOptions, $moduleOptions);
        assert('isset($actionParameters["key"]); /* Key must be set before this is called. */');
        $this->key = $actionParameters["key"];
        if (array_key_exists("run-if", $actionParameters)) {
            $this->runIfOptions = $actionParameters["run-if"];
        }
    }

    /**
     * Returns the key of the key-/value-pair.
     * @return string the key of the key-/value-pair.
     */
    protected function getKey()
    {
        return $this->key;
    }

    public abstract function getConfigFile();

    public function initTransaction()
    {
        return TransactionManager::getInstance()->createTransaction($this->getConfigFile(), "file");
    }

    public function whatWillBeDone()
    {
        $key = $this->getKey();
        $currentValue = $this->getCurrentValue($this->getKey());
        $newValue = $this->getValue();
        return L::Modules_ChangeConfig($key, var_export($currentValue, true), var_export($newValue, true), $this->getConfigFile());
    }

    /**
     * @inheritdoc
     */
    public function getProperty() {
        return $this->getKey();
    }

    /**
     * @inheritdoc
     */
    public function runIf()
    {
        $key = (!empty($this->runIfOptions) && array_key_exists("key",$this->runIfOptions)) ? $this->runIfOptions["key"] : $this->getKey();
        $value = (!empty($this->runIfOptions) && array_key_exists("value",$this->runIfOptions)) ? $value = $this->runIfOptions["value"] : $this->getValue();
        $this->runIfConditionText = L::RunIf_NothingToChangeAs(var_export($key,true), var_export($key,true), var_export($this->getCurrentValue($key),true));

        if (!empty($this->runIfOptions)) {
            $operation = (!empty($this->runIfOptions) && array_key_exists("operation", $this->runIfOptions)) ? $operation = $this->runIfOptions["operation"] : "ne";        // Default is "ne"
            switch ($operation) {
                case "eq":
                    return ($this->getCurrentValue($key) === $value);
                case "ne":
                    return ($this->getCurrentValue($key) !== $value);
            }
            // the upcoming operations must be specific for numeric values
            // cast value and getProperty to float if possible
            $currentValue = $this->getCurrentValue($key);
            if(!is_numeric($value)) throw new Exception("The provided run-if value ". var_export($value,true) . " is not numeric to perform the provided operation ".$operation);
            if(!is_numeric($currentValue)) throw new Exception("The current value for the run-if condition ". var_export($currentValue,true) . " is not numeric to perform the provided operation ".$operation);
            $currentValue = floatval($currentValue);
            $value = floatval($value);
            switch ($operation) {
                case "gt":
                    return ($currentValue < $value);
                case "ge":
                    return ($currentValue <= $value);
                case "lt":
                    return ($currentValue > $value);
                case "le":
                    return ($currentValue >= $value);
                default: throw new Exception("The provided Operation is not supported: $operation");
            }

        } else {
            // When current value is equal to the value we want to set, do not run the util.
            return ($this->getCurrentValue($this->getKey()) !== $this->getValue());
        }
    }

    /**
     * Returns the value of the specific configuration property at the current state (usually before any changes).
     * @param $key
     * @return mixed
     */
    protected abstract function getCurrentValue($key);

    /**
     * @inheritdoc
     */
    public function getRunIfCondition()
    {
        return $this->runIfConditionText;
    }

}