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

/**
 * Class DeleteTypo3ConfigFile - Deletes a Typo3ConfigFile which is located within the ConfigurationFolder.
 * @package php\utils\filesystem
 */
class DeleteTypo3ConfigFile extends DeleteFile
{

    private $file = null;

    /**
     * @inheritdoc
     */
    public function __construct($actionParameters, $sectionOptions, $moduleOptions)
    {
        parent::__construct($actionParameters, $sectionOptions, $moduleOptions);
        assert('isset($actionParameters["value"]); /* File must be set before this is called. */');
        $this->file = $moduleOptions["ConfigurationFolder"] . $actionParameters["value"];
    }

    /**
     * @inheritdoc
     */
    public function getFile()
    {
        return  $this->file;
    }

}