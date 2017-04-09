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

use php\core\configuration\Configuration;
use php\core\Scheduler;
use php\core\UtilLoader;
use php\io\Dialog;

require_once 'core/bootstrap.php';

$dialog = new Dialog();
$dialog->intro();
if (Configuration::getInstance()->isDryRun()) {
    $dialog->dryRun();
} else {
    $dialog->runtimeUser();
}

$utilLoader = new UtilLoader(Configuration::getInstance());
$modules = Configuration::getInstance()->getProperty("Hardening.IncludeModules");

$selectionMode = Configuration::getInstance()->getProperty("Dialog.SelectionMode");
$selected_modules = $dialog->selectModules($modules, $selectionMode);

Configuration::getInstance()->getLogger()->info(\L::Dialog_UserChoseModules(implode(",",$selected_modules)));
try
{
    $runUtils = $utilLoader->loadRunUtils($selected_modules);
    Scheduler::getInstance()->runHardeningModules($selected_modules, $runUtils);
    if (!Configuration::getInstance()->isDryRun()) {
        // Outro messages user that files has been backed up. Since no files are backed up in dry-run, we do not need to print this information here.
        $dialog->outro();
    }
}
catch (Exception $e)
{
    Configuration::getInstance()->getWriter()->writeError($e->getMessage());
    Configuration::getInstance()->getLogger()->error($e->getMessage());
}


