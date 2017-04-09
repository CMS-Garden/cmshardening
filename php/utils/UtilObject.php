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


namespace php\utils;

use \Exception;
use php\core\configuration\Configuration;
use php\core\Util;
use php\core\storage\NoTransaction;
use php\core\storage\TransactionManager;
use \L;
use php\io\Dialog;
use php\io\Writer;

/**
 * Base-Class to all Util-Classes.
 * Defines the standard-operations which are accessed by the scheduler.
 */
abstract class UtilObject
{

    /**
     * @var string Name of the action which is usually defined within the actionParameters.
     */
    protected $name = "";

    /**
     * @var null|string Description which is usually defined within the actionParameters.
     */
    protected $description = "";

    /**
     * @var string Value which is usually defined within the actionParameters.
     */
    private $value = "";

    /**
     * @var string Type which describes the type of the value-parameter. Type is usually defined within the actionParameters.
     */
    private $type = "";

    /**
     * @var \php\core\storage\Transaction Transaction which is usually defined within the sectionOptions.
     */
    private $transaction = null;

    /**
     * @var string The string-representation of the transaction which is used to initialize a valid transaction-object.
     */
    private $transactionString = "";

    /**
     * Constructs the util parsing the supplied parameters and options.
     * @param $actionParameters array the parameters of the action.
     * @param $sectionOptions array the options of the section.
     * @param $moduleOptions array the options of the module.
     */
    public function __construct($actionParameters, $sectionOptions, $moduleOptions)
    {
        if (isset($actionParameters['name']) && !is_null($actionParameters['name'])) {
            $this->name = $actionParameters['name'];
        }
        if (isset($actionParameters['description']) && !is_null($actionParameters['description'])) {
            $this->description = Util::resolveTranslationLabel($actionParameters['description']);
        }
        if (isset($actionParameters["value"]) && !is_null($actionParameters['value'])) {
            // Empty values are resolved later by the user. @see $this->resolveEmptyValues();
            $this->value = $actionParameters["value"];
        }
        if (isset($actionParameters['type']) && !is_null($actionParameters['type'])) {
            $this->type = $actionParameters['type'];
        }
        if (isset($sectionOptions['transaction'])) {
            $this->transactionString = $sectionOptions['transaction'];
        }
    }

    /**
     * Returns the unique name of the action or an empty string.
     * @return string a unique name of the action or an empty string.
     */
    public function getName()
    {
        return $this->name;
    }

    /**
     * Returns the description of the action.
     * @return string a description of the action.
     */
    public function getDescription()
    {
        return $this->description;
    }

    /**
     * Returns the value of the key-/value-pair.
     * @return string the value of the key-/value-pair.
     */
    protected function getValue()
    {
        return $this->value;
    }

    /**
     * Returns the type of the value-field.
     * @return string the type of the value-field.
     */
    public function getType()
    {
        return $this->type;
    }

    /**
     * Setup the action.
     */
    public function setup()
    {
        $this->transaction = $this->initTransaction($this->transactionString);
        try {
            $this->transaction->begin();
        } catch (Exception $e) {
            Configuration::getInstance()->getWriter()->writeError($e->getMessage());
        }
    }

    /**
     * Run the action.
     *
     * @return bool true, when the action was processed successfully, otherwise false.
     */
    public function run()
    {
        return true;
    }

    /**
     * Finish the action.
     */
    public function finish()
    {
        $this->transaction->commit();
    }

    /**
     * Alias for rollback.
     */
    public function cancel()
    {
        $this->rollback();
    }

    /**
     * Revert actions which were done during executing the run()-method.
     */
    public function rollback()
    {
        $this->transaction->rollback();
    }

    /**
     * Initializes the transaction by transforming the $transaction-string into a transaction-class.
     *
     * @param $transaction string identifier of a transaction
     * @return \php\core\storage\Transaction
     * @throws Exception when transaction-name is "utils:initTransaction" and the initTransaction-method is not overwritten by the child-class.
     */
    protected function initTransaction($transaction)
    {
        if (!is_null($transaction)) {
            if (is_string($transaction)) {
                if ($transaction === "utils:initTransaction") {
                    throw new Exception(get_called_class() . " should overwrite initTransaction.");
                }
                list($type, $name) = explode(":", $transaction);
                return TransactionManager::getInstance()->createTransaction($name, $type);
            } else {
                throw new Exception("Undefined state. Invalid transaction.");
            }
        }
        return new NoTransaction();
    }

    /**
     * Returns a string that describes what will be done when running the run() method. This is used to inform the user and to create log-entries
     * @return string
     */
    public abstract function whatWillBeDone();

    /**
     * Checks if there are any run-if configurations for this runUtil and verifies of the conditions are met. This method can be used to check if a certain condition is present before run the runUtil.
     * @example run-if: {value: "insecureValue", operation: "eq"} # This checks if the value of a property equals (eq) "insecureValue"
     * @return bool
     */
    public abstract function runIf();

    /**
     * This method returns a textual description of the condition to met in runIf(); This can be generated using the configuration in the run-if tree and proper language strings
     * @return string A textual description of the condition to met in runIf();
     */
    public abstract function getRunIfCondition();

    /**
     * Asks user to confirm running the action, when in interactive-mode is activated.
     * @return bool returns true when action should be run, otherwise false.
     */
    public function confirmRun()
    {
        if (Dialog::isInteractive()) {
            return Writer::YES == Configuration::getInstance()->getWriter()->promptUserYesNo(\L::Modules_UserConfirmation, Writer::YES);
        } else {
            return true;
        }
    }

    /**
     * The name of the property which is acted on.
     * @return string
     */
    public function getProperty() {
        return $this->getName();
    }

    /**
     * This methods resolves empty values by prompting the user for input.
     */
    public function resolveEmptyValues()
    {
        if (Util::is_null_or_empty($this->getValue())) {
            $this->value = Configuration::getInstance()->getWriter()->promptUserInput(L::Dialog_missingPropertyPrompt($this->getProperty()), $this->type);
            Configuration::getInstance()->getLogger()->info(L::Dialog_UserEntered(var_export($this->value,true)));
        }
    }
}