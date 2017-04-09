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

namespace php\core\configuration;


use Exception;
use \L;
use php\core\Util;

/**
 * Class TypeChecker
 * This class helps validating entered user data
 * @package php\core\configuration
 */
class TypeChecker
{

    /**
     * Creates a type-checker of the specified type.
     * @param $type string The type of the type-checker to be created.
     * @return TypeBoolean|TypeDirectory|TypeFile|TypeInteger|TypeString
     * @throws Exception when a not existing type was specified.
     */
    public static function create($type)
    {
        switch($type)
        {
            case "boolean":
                return new TypeBoolean();
            case "string":
                return new TypeString();
            case "integer":
                return new TypeInteger();
            case "file":
                return new TypeFile();
            case "directory":
                return new TypeDirectory();
            default:
                throw new Exception("The type '" . $type . "' is not known by the system.'");
        }
    }

}

/**
 * Base Class Type which defines an abstract check-method which should be implemented by all child-classes.
 * @package php\core\configuration
 */
abstract class Type
{
    private $description;

    /**
     * Type constructor.
     * @param $description string The description of the type. See child-classes for more information.
     */
    public function __construct($description)
    {
        $this->description = $description;
    }

    /**
     * Checks whether the supplied value is of this $type.
     * @param $value mixed the value which should be checked.
     * @return bool true, when the value is of this $type, otherwise false.
     */
    public abstract function check($value);

    /**
     * Returns the description of this type.
     * @return string The description of this type.
     */
    public function getDescription()
    {
        return $this->description;
    }
}

class TypeBoolean extends Type
{

    public function __construct()
    {
        parent::__construct("true/false");
    }

    public function check($value)
    {
        return Util::is_bool($value);
    }
}

class TypeString extends Type
{
    public function __construct()
    {
        parent::__construct(L::TypeChecker_String);
    }

    public function check($value)
    {
        return is_string($value);
    }
}

class TypeInteger extends Type
{
    public function __construct()
    {
        parent::__construct(L::TypeChecker_Integer);
    }

    public function check($value)
    {
        return Util::is_integer($value);
    }
}

class TypeFile extends Type
{
    public function __construct()
    {
        parent::__construct(L::TypeChecker_File);
    }

    public function check($value)
    {
        return is_file($value);
    }
}

class TypeDirectory extends Type
{
    public function __construct()
    {
        parent::__construct(L::TypeChecker_Directory(DIRECTORY_SEPARATOR));
    }

    public function check($value)
    {
        return Util::is_dir($value);
    }
}
