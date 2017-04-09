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

use ErrorException;
use php\core\configuration\Configuration;
use \L;

/**
 * Class UtilLoader loads and initializes all UtilObjects found within the configuration.
 * @package php\core
 */
class UtilLoader
{

    private $configuration;
    private $runIfConditions;

    /**
     * UtilLoader constructor.
     * @param $configuration \php\core\configuration\Configuration the initialized configuration-object.
     */
    public function __construct($configuration)
    {
        $this->configuration = $configuration;
        $this->runIfConditions = $this->initRunIfConditions();
    }

    /**
     * Setup RunIf-Conditions.
     * Asks the user for input when empty run-if-conditions are detected.
     */
    private function initRunIfConditions()
    {
        $runIfConditions = array();
        $runIfProperty = $this->configuration->getProperty("RunIf");
        if (!empty($runIfProperty)) {
            Configuration::getInstance()->getWriter()->writeHeadline(L::Dialog_GlobalRunIfHeadline);
            Configuration::getInstance()->getWriter()->write(L::Dialog_GlobalRunIf);
        }
        foreach ($runIfProperty as $key => $runIfCondition) {
            // If the required runIf value is not yet provided in the config.yml the user will be prompted for entering it.
            Configuration::getInstance()->getWriter()->write(""); // adds a newline to be more readable.
            $runIfConditions[$key] = $this->configuration->getProperty("RunIf." . $key);
        }
        return $runIfConditions;
    }

    /**
     * Loads all UtilObject's.
     *
     * @param $modules array which contains hardening-actions.
     * @return array of UtilObjects'.
     */
    public function loadRunUtils($modules)
    {
        Configuration::getInstance()->getWriter()->writeHeadline(L::Dialog_ModulQuestionaireHeadline);
        $utils = array();
        foreach ($modules as $module) {
            $moduleOptions = $this->getModuleOptions($module);
            $sectionsToRun = $this->configuration->getProperty(Util::configBuildPath($module, "RunSections"));
            if (isset($sectionsToRun)) {
                foreach ($sectionsToRun as $sectionToRun) {
                    $sectionOptions = $this->getSectionOptions($module, $sectionToRun);
                    if ($this->evaluateRunIfCondition($sectionOptions)) {
                        $runUtils = $this->configuration->getProperty(Util::configBuildPath($module, $sectionToRun, "RunUtils"));
                        if (isset($runUtils)) {
                            foreach ($runUtils as $action) {
                                $actionName = key($action);
                                $actionParameters = current($action);
                                array_push($utils, $this->initAction($actionName, $actionParameters, $sectionOptions, $moduleOptions));
                            }
                        }
                    }
                }
            }
        }
        return $utils;
    }

    /**
     * Retrieves the options of the specified module.
     * @param $module string the module where the options are located.
     * @return array of options. empty array when no module-options were found.
     */
    private function getModuleOptions($module)
    {
        $moduleOptions = $this->configuration->getProperty(Util::configBuildPath($module, "Options"));
        if (!is_null($moduleOptions)) {
            foreach ($moduleOptions as $moduleOptionName => $value) {
                $namespace = $module . "." . "Options" . "." . $moduleOptionName;
                $moduleOptions[$moduleOptionName] = $this->configuration->getProperty($namespace);
            }
            return $moduleOptions;
        } else {
            return array();
        }
    }

    /**
     * Retrieves the options of the specified section within the package-
     * @param $module string the module where the section is located.
     * @param $section string the section where the options are located.
     * @return array of options. empty array when no section-options were found.
     */
    private function getSectionOptions($module, $section)
    {
        $namespace = Util::configBuildPath($module, $section, "Options");
        if ($this->configuration->doesPropertyExist($namespace)) {
            return $this->configuration->getProperty($namespace);
        } else {
            return array();
        }
    }

    /**
     * Initializes a new command-object specified within the config.
     * @param $actionName string The name of the hardening action which identifies the class to handle the action: if actionName = <package>.<class> -> \php\utils\<package>\<class>
     * @param $actionParameters array An array of arguments for this action, e.g. key-value pair
     * @param $sectionOptions array An array of options which were specified within the section.
     * @param $moduleOptions array An array of options which were specified within the module.
     * @return \php\utils\UtilObject The UtilObject to handle the action
     * @throws ErrorException
     */
    public function initAction($actionName, $actionParameters, $sectionOptions, $moduleOptions)
    {
        $namespaceArray = explode(".", $actionName);
        if (sizeof($namespaceArray) != 2) {
            throw new ErrorException("The action '$actionName' is not defined properly. It should be in form of <package>.<class>");
        }
        list($package, $cls_name) = $namespaceArray;
        $cls = "php\\utils\\$package\\$cls_name";
        if (!class_exists($cls)) {
            throw new ErrorException("The action '$actionName' is not defined as class $cls.");
        }
        return new $cls($actionParameters, $sectionOptions, $moduleOptions);
    }

    /**
     * Evaluates the sections RunIf-Condition.
     * @param $sectionOptions array The section-options where the run-if-conditions are specified.
     * @return bool true, when the run-if-condition matches, otherwise false.
     */
    private function evaluateRunIfCondition($sectionOptions)
    {
        if (array_key_exists("run-if", $sectionOptions)) {
            $runIf = $sectionOptions["run-if"];
            $logicalOperator = "AND";
            if (array_key_exists("logicalOperator", $runIf)) {
                if (strtoupper($runIf["logicalOperator"]) === "OR")
                    $logicalOperator = "OR";
                unset($runIf["logicalOperator"]);
            }
            foreach ($runIf as $key => $runIfCondition) {
                if (array_key_exists($key, $this->runIfConditions)) {
                    if (RunIfCondition::create($runIfCondition)->evaluate($this->runIfConditions[$key])) {
                        if ($logicalOperator == "OR")
                            return true;
                    } else {
                        if ($logicalOperator == "AND")
                            return false;
                    }
                }
            }
            if ($logicalOperator == "OR")
                return false;
            if ($logicalOperator == "AND")
                return true;
        }
        return true;
    }

}