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
use Exception;
use \L;

/**
 * Class RunIfCondition
 *
 * @package php\core
 */
class RunIfCondition
{
    /**
     * @var string The operation which is used to test. Valid operations are:
     *
     * eq: true when $this->value matches value, otherwise false.
     * ne: true when $this->value does not match value, otherwise false.
     */
    private $operation;

    /**
     * @var mixed The value on which the evaluate-method operates on.
     */
    private $value;

    /**
     * Private RunIfCondition constructor.
     * Please use the static create-method instead.
     * @param $runIfOptions array the Options for the run-if conditions
     */
    private function __construct($runIfOptions)
    {
        $this->operation = !empty($runIfOptions["operation"]) ?  $runIfOptions["operation"] : "eq";        // Default is "eq"
        $this->value = $runIfOptions["value"];
    }

    /**
     * Creates an instance of the run-if-condition.
     * @param $runIfCondition array the run-if-condition as array containing an operation and a value.
     * @return RunIfCondition
     */
    public static function create($runIfCondition)
    {
        return new RunIfCondition($runIfCondition);
    }

    /**
     * Evaluates the supplied $value whether it matches with the run-if-condition.
     * @param $value
     * @return bool true, when the value matches the run-if-condition, otherwise false.
     * @throws Exception when the Operation of the run-if-condition's operator does not exist.
     */
    public function evaluate($value)
    {
        switch ($this->operation) {
            case "eq":
                return ($this->value === $value);
            case "ne":
                return ($this->value !== $value);
            default:
                throw new Exception(L::RunIf_InvalidCondition);
        }
    }

}
