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
use \L;
use php\core\configuration\Configuration;
use php\core\Util;

/**
 * Class FileTransaction
 * This class is a transaction for handling files. A Backup file is created and can be rolled back
 * @package php\core\storage
 */
class FileTransaction extends Transaction
{
    private $file_original;
    private $file_backup;
    private $noOriginalFile = false;

    public function __construct($name)
    {
        parent::__construct($name);
        $this->file_original = $name;
        $backupLocation = ROOT_PATH . Configuration::getInstance()->getProperty("Backup.BackupLocation");
        // create backupLocation in filesystem if not yet exist
        if (!file_exists($backupLocation))
            mkdir($backupLocation, 0700, true);
        $this->file_backup = $backupLocation . Configuration::getInstance()->getProperty("Backup.BackupFileNameSchema");
        $this->file_backup = str_replace(array(
            "%%filename%%",
            "%%date%%"
        ), array(
            basename($this->file_original),
            Util::nowForFiles()
        ), $this->file_backup);
        if (file_exists($this->file_original)) {
            $this->validateOriginalFile();
            $this->validateBackupFile();
        } else {
            $this->noOriginalFile = true;
        }
    }

    /**
     * Starts the transaction by creating a backup file of the given original file
     *
     * @see \php\core\storage\Transaction::begin()
     */
    public function begin()
    {
        parent::begin();
    }

    /**
     * Actually this method does nothing, Changes (hardening) are done on the original file, which are committed directly
     * @see \php\core\storage\Transaction::commit()
     */
    public function commit()
    {
        if (parent::commit()) {
        }
    }

    /**
     * To rollback any changes made in this transaction the backup file is written back over the original file
     * @see \php\core\storage\Transaction::rollback()
     */
    public function rollback()
    {
        $current_state = $this->state;
        if (parent::rollback()) {
            if (!$this->noOriginalFile) {
                # Write back the backup file
                copy($this->file_backup, $this->file_original);
            } else {
                if (file_exists($this->file_original)) {
                    # If there was no original file, delete the created one
                    unlink($this->file_original);
                }
            }
        } else {
            $this->state = $current_state;
        }
    }

    /**
     * {@inheritDoc}
     */
    protected function createBackup()
    {
        if (!$this->noOriginalFile) {
            $this->validateOriginalFile();
            $this->validateBackupFile();
            if (copy($this->file_original, $this->file_backup)) {
                self::getLogger()->info(L::Transaction_BackupCreated($this->file_backup));
                self::getWriter()->write(L::Transaction_BackupCreated($this->file_backup));
            } else {
                throw new Exception(L::Transaction_BackupFailed($this->file_backup));
            }
        }

    }

    public
    function getFileOriginal()
    {
        return $this->file_original;
    }

    public
    function getFileBackup()
    {
        return $this->file_backup;
    }

    private
    function validateOriginalFile()
    {
        if (!is_readable($this->file_original)) {
            throw new Exception(L::Transaction_FileNotAccessible($this->file_original));
        }
        if (!is_writable($this->file_original)) {
            throw new Exception(L::Transaction_FileNotWriteable($this->file_original));
        }
    }

    private
    function validateBackupFile()
    {
        if (file_exists($this->file_backup)) {
            throw new Exception(L::Transaction_BackupExists($this->file_backup));
        }
    }

}