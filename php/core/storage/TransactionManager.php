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

use Exception;
use L;
use php\core\configuration\Configuration;

/**
 * Class TransactionManager
 * This TransactionManager's purpose is to create proper transactions
 * @package php\core\storage
 */
class TransactionManager
{
    private $transactions;
    private static $instance = null;

    /**
     * Creates an instance of the TransactionManager class (Singleton pattern)
     *
     * @return \php\core\storage\TransactionManager
     */
    static public function getInstance()
    {
        if (null === self::$instance) {
            self::$instance = new self ();
        }
        return self::$instance;
    }

    /**
     * Constructor
     */
    private function __construct()
    {
        $this->transactions = array();
    }

    public function createTransaction($name, $type)
    {
        if (array_key_exists($name, $this->transactions))
            return $this->transactions [$name];
        $transaction = null;
        switch (strtoupper($type)) {
            case 'FILE' :
                $transaction = new FileTransaction ($name);
                break;
        }
        if (is_null($transaction))
            throw new Exception ("Transaction type not known: " . $type);
        $this->transactions [$name] = $transaction;
        return $transaction;
    }

    /**
     * Returns the array of all registered transactions
     * @return array
     */
    public function getTransactions()
    {
        return $this->transactions;
    }

    /**
     * @inheritDoc
     */
    public function __destruct()
    {
        //$this->rollBackAllTransactions();
    }

    /**
     * This method rolls back all began and committed transactions
     * @throws Exception
     */
    public function rollBackAllTransactions()
    {
        Configuration::getInstance()->getWriter()->write(L::Transaction_AllRolledBack);
        Configuration::getInstance()->getLogger()->warn(L::Transaction_AllRolledBack);
        foreach ($this->transactions as $transaction) {
            try {
                $transaction->rollback();
            } catch (Exception $e){
                Configuration::getInstance()->getWriter()->writeError($e->getMessage());
                Configuration::getInstance()->getLogger()->error($e->getMessage());
            }
        }
    }

    public function clearTransactions() {
        $this->transactions = array();
    }
}