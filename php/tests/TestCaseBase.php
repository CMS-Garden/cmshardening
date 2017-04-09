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


namespace php\tests;

/**
 * Class TestCaseBase - Base-Class for all TestCases which extends the PHPUnit_Framework_TestCase with further utils.
 * @package php\tests
 */
class TestCaseBase extends \PHPUnit_Framework_TestCase
{

    protected function getResourceFolder()
    {
        return realpath(dirname(__FILE__)) . DIRECTORY_SEPARATOR . "samples" . DIRECTORY_SEPARATOR;
    }

}