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


namespace php\utils\meta;


use L;
use php\core\configuration\Configuration;
use php\core\storage\NoTransaction;
use php\io\Dialog;
use php\io\Writer;
use php\utils\UtilObject;

/**
 * Class Description which has the task to print a description.
 * @package php\utils\meta
 */
class Description extends UtilObject
{

    /**
     * @inheritdoc
     */
    public function __construct($actionParameters, $sectionOptions, $moduleOptions)
    {
        parent::__construct($actionParameters,$sectionOptions,$moduleOptions);
        assert('isset($actionParameters["description"]); /* Description must be set before this is called. */');
    }


    /**
     * Checks if there are any run-if configurations for this runUtil and verifies of the conditions are met. This method can be used to check if a certain condition is present before run the runUtil.
     * @example run-if: {value: "insecureValue", operation: "eq"} # This checks if the value of a property equals (eq) "insecureValue"
     * @return bool
     */
    public function runIf()
    {
        return true;
    }

    /**
     * This method returns a textual description of the condition to met in runIf(); This can be generated using the configuration in the run-if tree and proper language strings
     * @return string A textual description of the condition to met in runIf();
     */
    public function getRunIfCondition(){}

    /**
     * This overwrites the resolveEmptyValues-method since no values to resolve.
     */
    public function resolveEmptyValues() {}

    /**
     * This overwrites the confirmRun-method since no user-interaction is required.
     *
     * @return bool returns true when action should be run, otherwise false.
     */
    public function confirmRun()
    {
        if (Dialog::isInteractive()) {
            return Writer::OK === Configuration::getInstance()->getWriter()->promptUserOk(L::Modules_UserConfirmationManualHardening);
        } else {
            return true;
        }
    }

    /**
     * This overwrites the initTransaction-method since no transaction is required.
     */
    public function initTransaction()
    {
        return new NoTransaction();
    }

    /**
     * Returns a string that describes what will be done when running the run() method. This is used to inform the user and to create log-entries
     * @return string
     */
    public function whatWillBeDone()
    {
        return L::Modules_WhatWillBeDoneManualHardening;
    }
}