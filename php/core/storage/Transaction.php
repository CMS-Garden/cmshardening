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

use php\core\configuration\Configuration;
use \L;
use \Exception;
use \LogicException;

/**
 * Class Transaction
 * Manages one transaction with its states. This class' purpose is to provide the possibility for committing and rolling back any changes.
 * @package php\core\storage
 */
abstract class Transaction
{

    public $state;

    protected $name;

    public function __construct($name)
    {
        $this->state = TransactionStates::Fresh;
        $this->name = $name;
        self::getLogger()->info(L::Transaction_TransactionCreated($this->name));
    }


    /**
     * Begins the transaction by at least creating a backup file
     * @return bool true if the begin action was actually performed. False if there was nothing to do
     * @throws Exception if the Transaction's state is not proper for begin()
     */
    public function begin()
    {
        if ($this->state === TransactionStates::Began) {
            return false;
        }
        if ($this->state !== TransactionStates::Fresh) {
            throw new LogicException("Cannot begin transaction " . $this->name . " as it is not in proper state ($this->state)");
        }
        $current_state = $this->state;
        try {
            self::getLogger()->info(L::Transaction_TransactionBegan($this->name));
            self::getWriter()->write(L::Transaction_TransactionBegan($this->name));
            $this->createBackup();
            $this->state = TransactionStates::Began;
        } catch (Exception $e) {
            self::getWriter()->writeError($e->getMessage());
            $this->state = $current_state;
            throw new Exception(L::Transaction_TransactionBeganFailed($this->name));
        }
        return true;
    }

    /**
     * Commits any changes made since begin()
     * @return bool true if the commit action was actually performed. False if there was nothing to do
     * @throws Exception if the Transaction's state is not proper for commit()
     */
    public function commit()
    {
        if ($this->state === TransactionStates::Commited) {
            return false;
        }
        if ($this->state !== TransactionStates::Began)
            throw new LogicException("Cannot commit transaction " . $this->name . " as it is not in proper state ($this->state)");
        $this->state = TransactionStates::Commited;
        self::getLogger()->info(L::Transaction_TransactionCommited($this->name));
        self::getWriter()->write(L::Transaction_TransactionCommited($this->name));
        return true;
    }

    /**
     * Rolls back any actions done in begin() or commit()
     * @return bool true if the rollback action was actually performed. False if there was nothing to do
     */
    public function rollback()
    {
        if ($this->state === TransactionStates::RolledBack) {
            return false;
        }
        if ($this->state == TransactionStates::Fresh)
            //throw new LogicException("Cannot roll back transaction " . $this->name . " as it is not in proper state ($this->state)");
            return false;
        $this->state = TransactionStates::RolledBack;
        self::getLogger()->info(L::Transaction_TransactionRolledBack($this->name));
        self::getWriter()->write(L::Transaction_TransactionRolledBack($this->name));
        return true;
    }

    /**
     * Generates a backup file within the backup-location based on the name filename-schema defined within the config.yml.
     * @throws Exception if creating a backup failed, e.g. because of laking file permissions
     */
    protected abstract function createBackup();

    /**
     * Returns a Logger for this class. This is simply a shortcut
     * @return \php\core\Logger
     */
    protected static function getLogger()
    {
        return Configuration::getInstance()->getLogger();
    }

    /**
     * Returns a Writer for this class. This is simply a shortcut
     * @return \php\io\Writer
     */
    protected static function getWriter()
    {
        return Configuration::getInstance()->getWriter();
    }
}