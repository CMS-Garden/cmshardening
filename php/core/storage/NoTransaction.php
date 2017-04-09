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


namespace php\core\storage;

/**
 * NullObject which is used within scheduler when no real transaction is necessary.
 * @package php\core\storage
 */
/**
 * Class NoTransaction
 * This class is a transaction which actually does nothing
 * @package php\core\storage
 */
class NoTransaction extends Transaction
{

    /**
     * This method does nothing but initializing the constructor of the parent class
     * NoTransaction constructor.
     */
    public function __construct()
    {
        parent::__construct("NoTransaction");
    }

    /**
     * Empty begin-step. Nothing to do here.
     */
    public function begin() {}

    /**
     * Empty commit-step. Nothing to do here.
     */
    public function commit() {}

    /**
     * Empty rollback-step. Nothing to do here.
     */
    public function rollback() {}

    /**
     * Empty create-backup-step. Nothing to do here.
     */
    protected function createBackup(){}
}