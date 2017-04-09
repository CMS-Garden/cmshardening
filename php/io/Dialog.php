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


namespace php\io;

use Exception;
use php\core\configuration\Configuration;
use php\core\Util;
use \L;
use php\io\i18n;

/**
 * Class Dialog
 * Handles the global dialog for users like script arguments, intro text, etc.
 * @package php\io
 */
class Dialog
{
    private $writer;
    public $possibleConfigurationArguments;
    public $possibleCallbackArguments;

    public function __construct()
    {
        $this->writer = Configuration::getInstance()->getWriter();

        $this->addPossibleConfigurationArgument(array("--checkOnly", "-c"), "HardeningSettings.CheckOnly");
        $this->addPossibleConfigurationArgument(array("--interactive", "-i"), "HardeningSettings.Interactive");
        $this->addPossibleConfigurationArgument(array("--silent", "-s"), "Dialog.Silent");
        $this->addPossibleCallbackArgument(array("--lang", "-l"), 'changeLanguage');
        $this->addPossibleCallbackArgument(array("--help", "-h", "--usage"), 'usage');
        // TODO: CLI argument to select the hardening module (joomla, typo3, wordpress)

        $this->handleArguments();

    }

    private function handleArguments()
    {
        if (Util::isCLI()) {
            $options = $this->parseServerArgv();

            // Find invalid Arguments and print an error message.
            $invalidArguments = array_diff_key($options, array_merge($this->possibleCallbackArguments, $this->possibleConfigurationArguments));
            if (sizeof($invalidArguments) > 0) {
                $this->writer->writeError(L::Dialog_CLIArgumentError(implode(", ", array_keys($invalidArguments))));
                $this->writer->write("");
                $this->writer->write(L::Dialog_usage);
                die(-183947);
            }
            // handle Callback Arguments
            foreach ($this->possibleCallbackArguments as $possibleCallbackArgument => $callback) {
                if (array_key_exists($possibleCallbackArgument, $options)) {
                    // calls the $callback function for the registered CallbackArgument with the parameters provided by the user as argument value
                    call_user_func(array($this, $callback), $options[$possibleCallbackArgument]);
                }
            }

            // handle Configuration Arguments
            foreach ($this->possibleConfigurationArguments as $possibleConfigurationArgument => $configurationKey) {
                if (array_key_exists($possibleConfigurationArgument, $options)) {
                    // Sets the appropriate configuration with the provided value
                    $value = $options[$possibleConfigurationArgument];
                    if (empty($value)) $value = true;
                    Configuration::getInstance()->setProperty($configurationKey, $value);
                }
            }
        } else {
            //TODO: Handle HTTP script parameter (e.g.: index.php?verbose=2&interactive=false)
        }
    }

    public function intro()
    {
        $this->writer->write(L::Dialog_ApplicationHeadline);
        $this->writer->writeHeadline(L::Dialog_IntroHeadline);
        $this->writer->write(L::Dialog_Intro);
        $this->writer->write("");
        $this->writer->writeHeadline(L::Dialog_WarningHeadling);
        $this->writer->write(L::Dialog_Warning);
        $this->writer->write("");
        $this->writer->write(L::Dialog_CancelNotification);
        $this->writer->write("");
    }


    public function runtimeUser()
    {
        if (!$this->writer->promptUserOKCancel(L::Dialog_RuntimeUser))
            exit();
        $this->writer->write("");
    }

    public function outro()
    {
        $this->writer->write(L::Dialog_BackupNotice(ROOT_PATH . Configuration::getInstance()->getProperty("Backup.BackupLocation")));
    }

    private function addPossibleConfigurationArgument($names, $configurationKey)
    {
        if (is_string($names)) $names = array($names);
        foreach ($names as $name) {
            $this->possibleConfigurationArguments[$name] = $configurationKey;
        }
    }

    private function addPossibleCallbackArgument($names, $callback)
    {
        if (is_string($names)) $names = array($names);
        foreach ($names as $name) {
            $this->possibleCallbackArguments[$name] = $callback;
        }
    }

    public function usage()
    {
        $this->writer->write(L::Dialog_usage);
        die();
    }

    public function changeLanguage($lang)
    {
        try {
            if ($lang !== i18n::getInstance()->getLang()) {
                i18n::getInstance()->setLang($lang);
                i18n::getInstance()->initialize();
            }
        } catch (Exception $e) {
            $this->writer->writeError($e->getMessage());
        }

    }

    /**
     * Parses the CLI arguments provided by $_SERVER['argv']
     * @return array The array contains the arguments as key and possible argument values as array values
     */
    private function parseServerArgv()
    {
        $options = array();
        $lastArgument = null;
        foreach (array_slice($_SERVER['argv'], 1) as $argument) {
            // argument begins with at least one -
            if (strpos($argument, "-") === 0) {
                // the argument contains a value which is separated by =
                if (strpos($argument, "=")) {
                    list($argName, $argValue) = explode("=", $argument);
                    $options[$argName] = $argValue;
                    $lastArgument = null;
                } // There is an argument, which has no value or the value is separated by space (the value is the next $argument
                else {
                    $options[$argument] = null;
                    $lastArgument = $argument;
                }
            } else {
                // in case this is no argument but a space-separated value
                if (is_null($lastArgument)) {
                    $this->writer->writeError(L::Dialog_CLIArgumentError($argument));
                    die();
                }
                $options[$lastArgument] = $argument;
                $lastArgument = null;
            }
        }
        return $options;
    }

    /**
     * Ask's user to select modules to run by the scheduler.
     *
     * @param $modules  array of module-names which can be selected
     * @param string $selectionMode the selection-mode, either single- or multi-selection possible.
     * @return array the selected module-names to run by the scheduler.
     * @throws Exception
     */
    public function selectModules($modules, $selectionMode = "single")
    {
        Configuration::getInstance()->getWriter()->writeHeadline(L::Dialog_ModuleSelectionHeadline);
        if ($selectionMode === "single") {
            return $this->selectModule($modules);
        } else if ($selectionMode === "multi") {
            return $this->writer->promptToChooseMultiple(L::Modules_selectModules, $modules);
        } else {
            throw new Exception(L::Dialog_missingProperty("Dialog.SelectionMode"));
        }
    }

    /**
     * Ask's user to select a module to run by the scheduler.
     *
     * @param $modules  array of module-names which can be selected
     * @return array    the selected module-name to run by the scheduler or an empty array.
     */
    public function selectModule($modules)
    {
        $index = $this->writer->promptToChoose(L::Modules_selectModules, $modules);
        if ($index < 0 || $index >= count($modules)) {
            return array();
        } else {
            return array($modules[$index]);
        }
    }

    /**
     *
     * @return bool True if the user wishes to be asked at any step. False if the user will only be asked if it is really necessary
     */
    public static function isInteractive()
    {
        return !(bool)Configuration::getInstance()->getProperty("Dialog.Silent");
    }

    /**
     * Prints information that dry-run is activated.
     * Requires the user to press the enter-key.
     */
    public function dryRun()
    {
        $this->writer->promptUserOk(L::Dialog_DryRun);
    }

}