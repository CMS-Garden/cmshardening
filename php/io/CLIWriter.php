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

use \L;
use php\core\configuration\Configuration;
use php\core\configuration\TypeChecker;
use php\core\Util;

define("LINE_LENGTH", 79);
// in case there is no STDIN, etc defined
if (!defined('STDIN')) define('STDIN', fopen('php://stdin', 'r'));
if (!defined('STDOUT')) define('STDOUT', fopen('php://stdout', 'w'));
if (!defined('STDERR')) define('STDERR', fopen('php://stderr', 'w'));

/**
 * Class CLIWriter
 * This class is the user interface for command lines
 * @package php\io
 */
class CLIWriter extends Writer
{
    /**
     * @inheritDoc
     */
    public
    function write($text)
    {
        $text = $this->str_format($text);
        fprintf(STDOUT, $text . PHP_EOL);
    }

    /**
     * @inheritDoc
     */
    public
    function writeHeadline($text)
    {
        $text = str_replace('§{n}', PHP_EOL . "| ", $text);
        $text = str_replace('§{t}', "\t", $text);
        if (strlen($text) > LINE_LENGTH - 2) {
            $text = substr($text, 0, LINE_LENGTH - 3) . PHP_EOL . "| " . substr($text, LINE_LENGTH - 3);
        }
        fprintf(STDOUT, PHP_EOL . "| " . $text . PHP_EOL . "+" . str_repeat("-", LINE_LENGTH - 1) . PHP_EOL);
    }

    /**
     * @inheritDoc
     */
    public function writeList($array)
    {
        foreach ($array as $el) {
            fprintf(STDOUT, "\t- " . $el . PHP_EOL);
        }
    }


    /**
     * @inheritDoc
     */
    public function writeError($text)
    {
        $text = $this->str_format($text);
        fprintf(STDERR, $text . PHP_EOL);
    }


    /**
     * @inheritDoc
     */
    public
    function promptUserYesNo($text, $default = null)
    {
        $text = $this->str_format($text);

        // Transform default value to either null or Writer::YES, Writer::NO.
        if ($default === null || empty($default)) {
            // No default value present.
            $default = null;
        }
        else if (Util::is_bool($default)) {
            // Boolean default value.
            $default = ((is_bool($default) && $default == true) || $default === "true") ? Writer::YES : Writer::NO;
        }
        else if ($default == Writer::YES || $default == Writer::NO) {
            // Nothing to do here.
        }
        else {
            // Can not correctly interpret default value. Log this issue and set default-value to null.
            Configuration::getInstance()->getLogger()->debug("Possible invalid default for promptUserYesNo '" . $default . "'!");
            $default = null;
        }

        while (true) {
            fprintf(STDOUT, $text);
            $choice = $this->generateUserOptionsToDisplay(array(Writer::YES => L::Writer_OptionYes, Writer::NO => L::Writer_OptionNo), $default);
            fprintf(STDOUT, $choice);
            try {
                $userInput = $this->handleUserInput(fgets(STDIN), array(L::Writer_OptionYes, L::Writer_OptionNo));
                switch ($userInput) {
                    case L::Writer_OptionYes:
                        return true;
                    case L::Writer_OptionNo:
                        return false;
                    case "":
                        // User entered no value and pressed enter.
                        if ($default === null || empty($default)) {
                            // No default value present. Try again.
                            continue;
                        }
                        if ($default == Writer::YES || $default == Writer::NO) {
                            // Default value seems to be a constant. Print matching translation and return matching boolean.
                            Configuration::getInstance()->getWriter()->write(($default == Writer::YES) ? L::Writer_OptionYes : L::Writer_OptionNo);
                            return ($default == Writer::YES);
                        }
                        // This should not happen. Log this issue and let user try again.
                        Configuration::getInstance()->getLogger()->debug("Possible invalid default for promptUserYesNo '" . $default . "'!");
                        continue;
                }
            } catch (\Exception $e) {
                // Log unknown exception and continue.
                Configuration::getInstance()->getLogger()->debug("An unknown exception was triggered within promptUserYesNo: " . $e->getMessage());
                continue;
            }
        }
        return null;
    }

    /**
     * @inheritDoc
     */
    public
    function promptUserOk($text)
    {
        $text = $this->str_format($text);
        while (true) {
            fprintf(STDOUT, $text);
            $choice = $this->generateUserOptionsToDisplay(array(Writer::OK => L::Writer_OptionOK), Writer::OK);
            fprintf(STDOUT, $choice);
            try {
                $userInput = $this->handleUserInput(fgets(STDIN), array(L::Writer_OptionOK));
                switch ($userInput) {
                    case L::Writer_OptionOK:
                        return true;
                    case null:
                        Configuration::getInstance()->getWriter()->write(L::Writer_OptionOK);
                        return (Writer::OK);
                }
            } catch (\Exception $e) {
                continue;
            }
        }
    }

    /**
     * @inheritDoc
     */
    public
    function promptUserOKCancel($text, $default = Writer::OK)
    {
        $text = $this->str_format($text);
        while (true) {
            fprintf(STDOUT, $text);
            $choice = $this->generateUserOptionsToDisplay(array(Writer::OK => L::Writer_OptionOK, Writer::CANCEL => L::Writer_OptionCancel), $default);
            fprintf(STDOUT, $choice);
            try {
                $userInput = $this->handleUserInput(fgets(STDIN), array(L::Writer_OptionOK, L::Writer_OptionCancel));
                switch ($userInput) {
                    case L::Writer_OptionOK:
                        return true;
                    case L::Writer_OptionCancel:
                        return false;
                    case null:
                        // When pressing enter, display and return default choice.
                        Configuration::getInstance()->getWriter()->write(($default == Writer::OK) ? L::Writer_OptionOK : L::Writer_OptionCancel);
                        return ($default == Writer::OK);
                }
            } catch (\Exception $e) {
                continue;
            }
        }
        return null;
    }

    /**
     * @inheritDoc
     */
    public
    function promptUserInput($text, $type = "", $default = "")
    {
        if (!empty($type)) {
            if($type==="boolean"){
                return $this->promptUserYesNo($text, $default);
            }
            $typeChecker = TypeChecker::create($type);
            do {
                $value = $this->_promptUserInput($text, $typeChecker->getDescription(), $default);
            } while (!$typeChecker->check($value));
        } else {
            $value = $this->_promptUserInput($text, "", $default);
        }
        return $value;
    }

    private
    function _promptUserInput($text, $typeDescription, $default)
    {
        $text = $this->str_format($text);
        fprintf(STDOUT, PromptUserInputText::create($text, $typeDescription, $default));
        $return = trim(fgets(STDIN));
        if (Util::is_null_or_empty($return)) return $default;
        switch ($return) {
            case "false" :
                return false;
            case "true" :
                return true;
            case ((string)intval($return)) :
                return intval($return);
            case ((string)floatval($return)) :
                return floatval($return);
        }
        return $return;
    }

    /**
     * @inheritDoc
     */
    public function promptToChoose($text, $array)
    {
        $text = $this->str_format($text);
        fprintf(STDOUT, $text . PHP_EOL);
        $array = array_values($array);
        foreach ($array as $k => $v) {
            fprintf(STDOUT, "  [$k] $v" . PHP_EOL);
        }
        while (true) {
            fprintf(STDOUT, L::Writer_choose);
            $return = trim(fgets(STDIN));
            if (array_key_exists($return, $array)) return $return;
        }
        return null;
    }

    /**
     * @inheritDoc
     */
    public function promptToChooseMultiple($text, $array)
    {
        $text = $this->str_format($text);
        fprintf(STDOUT, $text . PHP_EOL);
        $arrayToPrint = array_values($array);   // create unassociated Array so that the items have numbers as keys
        foreach ($arrayToPrint as $k => $v) {
            fprintf(STDOUT, "  [$k] $v" . PHP_EOL);
        }
        while (true) {
            fprintf(STDOUT, PHP_EOL . L::Writer_chooseMultiple);
            $input = trim(fgets(STDIN));
            if (strlen(trim($input)) === 0) continue;
            $returnArray = array();
            foreach (explode(",", $input) as $item) {
                $item = trim($item);
                if (array_key_exists($item, $arrayToPrint)) {
                    $arrayKey = array_keys($array)[$item];
                    $returnArray[] = $array[$arrayKey];
                }
            }
            if (sizeof($returnArray) == sizeof(explode(",", $input)))
                return $returnArray;
        }
        return null;
    }

    /**
     * Formats special characters within a string.
     *
     * Following table lists the special-characters and their mapping:
     *
     * Special-Character | Mapping
     *      ${n}$        | \n
     *      ${t}$        | \t
     *
     * @param $text string containing special-characters.
     * @return string the formatted text.
     */
    private function str_format($text)
    {
        $text = str_replace('§{n}', PHP_EOL, $text);
        $text = str_replace('§{t}', "\t", $text);
        return $text;
    }

    /**
     * Based on the valid user options the user input is parsed
     * @param $userInput    string The input provided by the user
     * @param $validUserOptions array all the possible strings that the user could have entered. Usually a string of the language files.
     * @return string   one of the provided $validUserOptions or null if entered string is empty
     * @throws \Exception   In case the user entered a string that cannot be matched to one of the $validUserOptions
     */
    private function handleUserInput($userInput, $validUserOptions)
    {
        $shouldSkipFirstLetter = $this->shouldSkipFirstLetterOfOptions($validUserOptions);
        $userInput = strtolower(trim($userInput));
        if ($userInput === "") return null;
        foreach ($validUserOptions as $validUserOption) {
            if (strtolower($validUserOption) === $userInput)
                return $validUserOption;
            if (!$shouldSkipFirstLetter && strtolower(substr($validUserOption, 0, 1)) === $userInput)
                return $validUserOption;
        }
        throw new \Exception('The entered Input does not match any valid Option');
    }

    /**
     * Generates a String of possible Options the user can enter. Hereby it is possible to mark the first letter, if this is distinct.
     * @param $userOptions array all the user-options as associated array (e.g. Writer::OK => L::Writer_OptionOK)
     * @param $default  int the option which is default (user can enter nothing -> this option) is highlighted by capital letters
     * @return string   Returns a string with all user options in a formated way
     */
    private function generateUserOptionsToDisplay($userOptions, $default)
    {
        $shouldSkipFirstLetter = $this->shouldSkipFirstLetterOfOptions($userOptions);
        foreach ($userOptions as $userOption => &$userOptionText) {
            if ($userOption == $default || $userOptionText == $default) {
                $userOptionText = strtoupper($userOptionText);
            }
            if(!$shouldSkipFirstLetter) {
                $userOptionText = "(" . substr($userOptionText, 0, 1) . ")" . substr($userOptionText, 1);
            }
        }
        return "[" . implode("/", $userOptions) . "] : ";
    }

    /**
     * Checks if the first letter of the userOptions occur more than once. This function is used to decide if the user can enter the first letter of the option as a shourtcut.
     * @param $userOptions array the array of all valid user options (yes, no, ok, cancel, etc.)
     * @return bool returns true if there is a character multiple times as the first character. False if all first characters occur only once.
     */
    private function shouldSkipFirstLetterOfOptions($userOptions)
    {
        $firstLetters = array();
        foreach ($userOptions as $userOption) {
            $firstLetter = strtolower(substr($userOption, 0, 1));
            if (in_array($firstLetter, $firstLetters))
                return true;
            $firstLetters[] = $firstLetter;
        }
        return false;
    }
}

/**
 * Class PromptUserInputText constructs a message which should be displayed to the user
 * @package php\io
 */
class PromptUserInputText
{

    private $message;

    /**
     * @see create
     * @param $text string The description-text or the question to ask the user.
     * @param $typeDescription string $typeDescription An optional type-description which specifies which user-input should be accepted.
     * @param $default string $default An optional default-value which specifies what should be returned when the user does not input any data.
     **/
    private function __construct($text, $typeDescription, $default)
    {
        $this->message = $this->initMessage($text, $typeDescription, $default);
    }

    /**
     * Creates and returns the message which should be displayed to the user.
     *
     * Example-Output:
     * <ul>
     * <li> "text (type) [default]:" when typeDescription and default is not empty</li>
     * <li> "text (type):" when typeDescription is not empty</li>
     * <li> "text [default]:" when default is not empty</li>
     * <li> "text:"</li>
     * </ul>
     * @param $text string The description-text or the question to ask the user.
     * @param $typeDescription string $typeDescription An optional type-description which specifies which user-input should be accepted.
     * @param $default string $default An optional default-value which specifies what should be returned when the user does not input any data.
     * @return string The message which should be displayed to the user.
     */
    public static function create($text, $typeDescription = "", $default = "")
    {
        $cls = new PromptUserInputText($text, $typeDescription, $default);
        return $cls->getMessage();
    }

    /**
     * Initializes the message which should be displayed to the user.
     * @param $text string The description-text or the question to ask the user.
     * @param $typeDescription string $typeDescription An optional type-description which specifies which user-input should be accepted.
     * @param $default string $default An optional default-value which specifies what should be returned when the user does not input any data.
     * @return string The message which should be displayed to the user.
     */
    private function initMessage($text, $typeDescription, $default)
    {
        $message = $text;
        if (!empty($typeDescription)) {
            $message .= " ($typeDescription)";
        }
        if (!empty($default)) {
            $message .= " [" . $default . "]";
        }
        $message .= ": ";
        return $message;
    }

    /**
     * Returns the message which should be displayed to the user.
     * @return string The message which should be displayed to the user.
     */
    public function getMessage()
    {
        return $this->message;
    }
}