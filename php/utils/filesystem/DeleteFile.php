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


namespace php\utils\filesystem;

use php\core\storage\NoTransaction;
use php\core\storage\TransactionManager;
use php\core\Util;
use php\utils\UtilObject;

/**
 * Class DeleteFile - Backup and remove a file (with the ability to rollback the backup-file).
 * @package php\utils\filesystem
 */
class DeleteFile extends UtilObject
{

    private $runIfConditionText = "";

    public function __construct($actionParameters, $sectionOptions, $moduleOptions)
    {
        parent::__construct($actionParameters, $sectionOptions, $moduleOptions);
    }

    /**
     * Removes the specified file when present.
     */
    public function run()
    {
        if (parent::run())
        {
            if (file_exists($this->getFile()))
            {
                unlink($this->getFile());
            }
        }
    }

    /**
     * Returns the file which should be deleted.
     * @return string the file which should be deleted.
     */
    public function getFile() {
        return $this->getValue();
    }

    /**
     * Overwrites the initTransaction-method to either return a file- or a no-transaction-object when the file does not exist.
     * @return \php\core\storage\FileTransaction|NoTransaction a FileTransaction when the file exists, otherwise a NoTransaction.
     */
    public function initTransaction()
    {
        $file = $this->getFile();
        if (file_exists($file))
        {
            return TransactionManager::getInstance()->createTransaction($file, "file");
        }
        else
        {
            // Avoid creating a transaction for a not existing file.
            return new NoTransaction();
        }
    }

    /**
     * Checks if there are any run-if configurations for this runUtil and verifies of the conditions are met. This method can be used to check if a certain condition is present before run the runUtil.
     * @example run-if: {value: "insecureValue", operation: "eq"} # This checks if the value of a property equals (eq) "insecureValue"
     * @return bool
     */
    public function runIf() {
        $should_run = file_exists($this->getFile());
        if (!$should_run) {
            $this->runIfConditionText = \L::RunIf_FileAlreadyDeleted($this->getFile());
        }
        return $should_run;
    }

    /**
     * This methods resolves empty values by prompting the user for input.
     */
    public function resolveEmptyValues() {}

    /**
     * Returns a string that describes what will be done when running the run() method. This is used to inform the user and to create log-entries
     * @return string
     */
    public function whatWillBeDone()
    {
        return \L::Modules_DeleteFile($this->getFile());
    }

    /**
     * This method returns a textual description of the condition to met in runIf(); This can be generated using the configuration in the run-if tree and proper language strings
     * @return string A textual description of the condition to met in runIf();
     */
    public function getRunIfCondition()
    {
        return $this->runIfConditionText;
    }
}