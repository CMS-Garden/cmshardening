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

use \L;
use php\core\configuration\Configuration;
use php\core\storage\TransactionManager;
use php\io\Writer;

/**
 * Executes the hardening-actions within the directory "packages".
 *
 * @package php\core
 */
class Scheduler
{

    private function __construct()
    {
        // Private constructor. Use getInstance() instead.
    }

    private static $instance = null;

    /**
     * Creates an instance of the Scheduler class (Singleton pattern)
     *
     * @return \php\core\Scheduler
     */
    static public function getInstance()
    {
        if (null === self::$instance) {
            self::$instance = new self ();
        }
        return self::$instance;
    }

    public function runHardeningModules($modules, $runUtils)
    {
        Configuration::getInstance()->getWriter()->writeHeadline(L::Modules_setupModule(implode(", ", $modules)));
        Configuration::getInstance()->getLogger()->info(L::Modules_setupModule(implode(", ", $modules)));
        $this->doSetup($runUtils);

        Configuration::getInstance()->getWriter()->writeHeadline(L::Modules_startModule(implode(", ", $modules)));
        Configuration::getInstance()->getLogger()->info(L::Modules_startModule(implode(", ", $modules)));
        $this->doRun($runUtils);

        Configuration::getInstance()->getWriter()->writeHeadline(L::Modules_finishModule(implode(", ", $modules)));
        Configuration::getInstance()->getLogger()->info(L::Modules_finishModule(implode(", ", $modules)));
        $this->doFinish($runUtils);

        $this->doCancelIfRequired($runUtils);
    }

    /**
     * Initiates the setup-step of all actions.
     * @param $runUtils array the actions to run.
     */
    protected function doSetup($runUtils)
    {
        if (!Configuration::getInstance()->isDryRun()) {
            foreach ($runUtils as $runUtil) {
                $runUtil->setup();
            }
        }
    }

    /**
     * Initiates the run-step of all actions.
     * @param $runUtils array the actions to run.
     */
    protected function doRun($runUtils)
    {
        foreach ($runUtils as $runUtil) {
            Configuration::getInstance()->getWriter()->writeHeadline(L::Modules_HardeningActionHeadline(Util::resolveTranslationLabel($runUtil->getName())));
            Configuration::getInstance()->getLogger()->info(L::Modules_HardeningActionHeadline(Util::resolveTranslationLabel($runUtil->getName())));

            if (!empty($runUtil->getDescription())) {
                Configuration::getInstance()->getWriter()->write($runUtil->getDescription());
            }
            $runUtil->resolveEmptyValues();

            if ($runUtil->runIf()) {

                $whatWillBeDone = $runUtil->whatWillBeDone();
                Configuration::getInstance()->getWriter()->write("§{n}" . $whatWillBeDone . "§{n}");
                Configuration::getInstance()->getLogger()->info($whatWillBeDone);

                // Document the current run for the user and the logs
                if (Configuration::getInstance()->isDryRun()) {
                    // Do not run util in dry-mode. Goto next util instead.
                    continue;
                } else if ($runUtil->confirmRun()) { // Prompt the user to confirm the change
                    // Perform the actual change
                    $runUtil->run();
                } else {
                    // Log that the user canceled to change this particular runUtil
                    Configuration::getInstance()->getLogger()->info(L::Modules_UserCanceledAction($runUtil->getName()));
                }
            } else {
                // If there is nothing to change
                Configuration::getInstance()->getWriter()->write($runUtil->getRunIfCondition());
                Configuration::getInstance()->getLogger()->info($runUtil->getRunIfCondition());
            }
        }
    }

    /**
     * Initiates the finish-step for all actions.
     * @param $runUtils array The actions to run.
     */
    protected function doFinish($runUtils)
    {
        if (!Configuration::getInstance()->isDryRun()) {
            foreach ($runUtils as $runUtil) {
                $runUtil->finish();
            }
        }
    }

    /**
     * @param $runUtils
     */
    protected function doCancelIfRequired($runUtils)
    {
        if (!Configuration::getInstance()->isDryRun()) {
            // Ask the user if still everything works. Otherwise roll back all actions
            Configuration::getInstance()->getWriter()->writeHeadline(L::Scheduler_sanityCheck);
            Configuration::getInstance()->getLogger()->info(L::Scheduler_sanityCheck);

            $userWishesRollback = Configuration::getInstance()->getWriter()->promptUserYesNo(L::Scheduler_ShallRollback);
            if ($userWishesRollback) {
                Configuration::getInstance()->getWriter()->write(L::Scheduler_sanityCheckCanceled);
                Configuration::getInstance()->getLogger()->warn(L::Scheduler_sanityCheckCanceled);
                TransactionManager::getInstance()->rollBackAllTransactions();
            } else {
                Configuration::getInstance()->getWriter()->write(L::Scheduler_sanityCheckCommitted);
                Configuration::getInstance()->getLogger()->warn(L::Scheduler_sanityCheckCommitted);
            }
        }
    }
}