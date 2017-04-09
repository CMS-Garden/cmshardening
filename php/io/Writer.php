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


namespace php\io;


/**
 * Class Writer
 * This is an abstract class, which shall be treated as interface. Derived from this a CLI interface is implemented and a web interface is possible.
 * @package php\io
 */
abstract class Writer
{
    const OK = 1;
    const YES = 2;
    const NO = 3;
    const CANCEL = 4;

    /**
     * Writes the text in a plain format to the output and appends a newline.
     * @param $text string The text to be written
     * @return void
     */
    public abstract function write($text);

    /**
     * Writes the text in a headline format to the output
     * @param $text string The text to be written
     * @return void
     */
    public abstract function writeHeadline($text);

    /**
     * Lists elements to the output
     * @param $array array The array of elements which should be listed
     * @return void
     */
    public abstract function writeList($array);

    /**
     * Writes the text in a error format to the output
     * @param $text string The text to be written
     * @return void
     */
    public abstract function writeError($text);

    /**
     * Asks the user to choose for "Yes" or "No"
     * @param $text string The text to be written to ask the user
     * @param int $default The Default value, to shorten the users answers
     * @return boolean  integer mapped on the constants of this class
     */
    public abstract function promptUserYesNo($text, $default = null);

    /**
     * Asks the user to choose for "Yes" or "No" or "Cancel"
     * @param $text string The text to be written to ask the user
     * @param int $default The Default value, to shorten the users answers
     * @return boolean  integer mapped on the constants of this class
     */
    public abstract function promptUserOKCancel($text, $default = Writer::OK);

    /**
     * Asks the user to press [Enter] to continue.
     * @param $text string The text to be written to ask the user
     * @return bool integer mapped on the constants of this class
     */
    public abstract function promptUserOk($text);

    /**
     * Asks the user to enter input.
     * @param $text string The text to be written to ask the user
     * @param string $type The type of the user-input which will be accepted. When type is empty all user-input is accepted.
     * @param string $default The default value which will be returned when a user does not input any data.
     * @return mixed The entered input or the default value, when user did not input any data.
     */
    public abstract function promptUserInput($text, $type = "", $default = "");

    /**
     * Asks the user to enter a string
     * @param $text string The text to be written to ask the user
     * @param $array array An array of options the user can choose of
     * @return int  The index of the array element the user chose
     */
    public abstract function promptToChoose($text, $array);

    /**
     * Asks the user to enter a string
     * @param $text string The text to be written to ask the user
     * @param $array array An array of options the user can choose of
     * @return array  The unassociated array of all elements the user chose. If the user only chose 1 element an array with one item is returned.
     */
    public abstract function promptToChooseMultiple($text, $array);
}