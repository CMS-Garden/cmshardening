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

use L;
use php\parser\Typo3ConfigParser;
use \Exception;

/**
 * Writes an key-value-pair into a Typo3-Config-File.
 */
class Typo3ConfigFileEntry extends ConfigFileEntry
{

    private $configFile;

    /**
     * @inheritdoc
     */
    public function __construct($actionParameters, $sectionOptions, $moduleOptions)
    {
        parent::__construct($actionParameters, $sectionOptions, $moduleOptions);
        $configFile = $moduleOptions["ConfigurationFolder"] . $moduleOptions["ConfigurationFile"];
        if (!file_exists($configFile))
        {
            throw new Exception(L::Error_FileNotExists($configFile));
        }
        else
        {
            $this->configFile = $configFile;
        }
    }

    /**
     * @inheritdoc
     */
    public function run()
    {
        if (parent::run())
            Typo3ConfigParser::getInstance()->setProperty(parent::getKey(), parent::getValue());
    }

    /**
     * @inheritdoc
     */
    public function getConfigFile()
    {
        return $this->configFile;
    }

    /**
     * @inheritdoc
     */
    protected function getCurrentValue($key)
    {
        return Typo3ConfigParser::getInstance()->getProperty($key);
    }
}