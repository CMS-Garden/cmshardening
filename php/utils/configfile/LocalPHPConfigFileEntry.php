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


use \Exception;
use php\core\configuration\Configuration;
use php\parser\HtAccessParser;
use php\parser\PHPUserIniParser;
use php\core\storage\TransactionManager;
use \L;

/**
 * Class LocalPHPConfigFileEntry
 * This class is a ConfigFileEntry that wraps a .htaccess and .user.ini util as there shall only be one runutil in the yaml file for both cases.
 * @package php\utils\configfile
 */
class LocalPHPConfigFileEntry extends ConfigFileEntry
{
    private $localPHPConfigFile;
    private $configFileEntry;
    private $path;

    public function __construct(array $actionParameters, array $sectionOptions, array $moduleOptions)
    {
        parent::__construct($actionParameters, $sectionOptions, $moduleOptions);
        // Find out what directory should be protected
        $PHPRootPathPropertyPath = $moduleOptions['ModulePrefix'] . '.Options.PHPLocalConfigPath';
        if (Configuration::getInstance()->doesPropertyExist($PHPRootPathPropertyPath)) {
            $this->path = Configuration::getInstance()->getProperty($PHPRootPathPropertyPath);
        } else {
            $RootPathDefault = null;
            if (array_key_exists("RootPath", $moduleOptions))
                $RootPathDefault = $moduleOptions["RootPath"];
            else if (array_key_exists("ConfigurationFile", $moduleOptions))
                $RootPathDefault = dirname($moduleOptions["ConfigurationFile"]) . DIRECTORY_SEPARATOR;
            else $RootPathDefault = ROOT_PATH . DIRECTORY_SEPARATOR;

            $this->path = Configuration::getInstance()->getWriter()->promptUserInput(L::PHP_LocalConfigPath, "directory", $RootPathDefault);
            Configuration::getInstance()->setProperty($PHPRootPathPropertyPath, $this->path);
        }

        if (Configuration::getInstance()->getProperty("RunIf.phpUserIni") === true) {
            $this->localPHPConfigFile = realpath($this->path) . DIRECTORY_SEPARATOR . ini_get('user_ini.filename');
        } else if (Configuration::getInstance()->getProperty("RunIf.phpHtAccess") === true) {
            $this->localPHPConfigFile = realpath($this->path) . DIRECTORY_SEPARATOR . '.htaccess';
        }
    }

    public
    function getConfigFile()
    {
        return $this->localPHPConfigFile;
    }

    /**
     * @inheritdoc
     */
    public function run()
    {
        if (!$this->configFileEntry)
            $this->configFileEntry = $this->getConfigParser();
        $this->configFileEntry->setProperty(parent::getKey(), parent::getValue());
    }

    /**
     * @inheritDoc
     */
    protected
    function getCurrentValue($key)
    {
        // Identify if .user.ini or .htaccess has to be used to harden the php configuration in a local directory
        if (!$this->configFileEntry)
            $this->configFileEntry = $this->getConfigParser();
        return $this->configFileEntry->getProperty($key);
    }

    public
    function initTransaction()
    {

        return TransactionManager::getInstance()->createTransaction($this->getConfigFile(), "file");
    }

    /**
     * Identify if .user.ini or .htaccess has to be used to harden the php configuration in a local directory
     * @return \php\parser\ConfigParser Returns an instance of ConfigParser or null if it is not possible to harden PHP on a per-directory basis
     * @throws \Exception if neither phpHtAccess nor phpUserIni is selected. In this case the run-if condition of the yaml section should have prevented this
     */
    private
    function getConfigParser()
    {
        # if both .htaccess and .user.ini fits (which actually should not be possible) use .user.ini as this cannot result in server errors
        if (Configuration::getInstance()->getProperty("RunIf.phpUserIni") === true) {
            if (empty($this->localPHPConfigFile)) $this->localPHPConfigFile = realpath($this->path) . DIRECTORY_SEPARATOR . ini_get('user_ini.filename');
            return PHPUserIniParser::getInstance($this->localPHPConfigFile);
        } else if (Configuration::getInstance()->getProperty("RunIf.phpHtAccess") === true) {
            if (empty($this->localPHPConfigFile)) $this->localPHPConfigFile = realpath($this->path) . DIRECTORY_SEPARATOR . '.htaccess';
            return HtAccessParser::getInstance($this->localPHPConfigFile);
        }
        # if both .htaccess and .user.ini fits (which actually should not be possible)
        throw new \Exception("ERROR: You have reached a code point that should not have been reached. Please check the run-if condition of the current section in the yaml file");

    }

}