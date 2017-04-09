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

namespace php\tests\utils\file;

require_once 'core/bootstrap.php';
use php\tests\TestCaseBase;
use php\utils\filesystem\DeleteTypo3ConfigFile;

class DeleteTypo3ConfigFileTest extends TestCaseBase
{
    public function setUp()
    {
        touch($this->getTestFile());
    }

    public function tearDown()
    {
        if (file_exists($this->getTestFile()))
        {
            unlink($this->getTestFile());
        }
    }

    private function getTestFile()
    {
        return $this->getResourceFolder() . "file-to-delete.txt";
    }


    public function testRun_DeletesConfigFile()
    {
        $actionParameters = array(
            "type" => "file",
            "value" => basename($this->getTestFile())
        );
        $sectionOptions = array(

        );
        $moduleOptions = array(
            "ConfigurationFolder" => $this->getResourceFolder()
        );
        $action = new DeleteTypo3ConfigFile(
            $actionParameters,
            $sectionOptions,
            $moduleOptions
        );

        $this->assertFileExists($this->getTestFile());
        $action->run();
        $this->assertFileNotExists($this->getTestFile());
    }

    public function testRun_WhenConfigFileDoesNotExist_Succeeds()
    {
        $not_existing_file = "not-existing-file.txt";
        $actionParameters = array(
            "type" => "file",
            "value" => $not_existing_file
        );
        $sectionOptions = array(

        );
        $moduleOptions = array(
            "ConfigurationFolder" => $this->getResourceFolder()
        );
        $action = new DeleteTypo3ConfigFile(
            $actionParameters,
            $sectionOptions,
            $moduleOptions
        );

        $this->assertFileNotExists($not_existing_file);
        $action->setup();
        $action->run();
        $this->assertFileNotExists($not_existing_file);
    }

    public function testRun_AfterRun_WhenRollbackWasTriggered_FileExistsAgain()
    {
        $actionParameters = array(
            "type" => "file",
            "value" => basename($this->getTestFile())
        );
        $sectionOptions = array(

        );
        $moduleOptions = array(
            "ConfigurationFolder" => $this->getResourceFolder()
        );
        $action = new DeleteTypo3ConfigFile(
            $actionParameters,
            $sectionOptions,
            $moduleOptions
        );

        $this->assertFileExists($this->getTestFile());
        $action->setUp();
        $action->run();
        $this->assertFileNotExists($this->getTestFile());
        $action->rollback();
        $this->assertFileExists($this->getTestFile());
    }



}