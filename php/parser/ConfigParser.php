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


namespace php\parser;

/**
 * Class ConfigParser
 * This abstract class describes the interface for a generic configuration parser
 *
 * @package php\parser
 * @author Falk Huber
 */
abstract class ConfigParser
{

    /**
     * Returns a Property after parsing the corresponding Configuration file
     *
     * @param string $key
     *            The key or name of the property to retrieve
     * @return string|null The value of the found property. If not found null is returned.
     */
    public abstract function getProperty($key);

    /**
     * Sets a properties value in the corresponding Configuration file.
     * If the property is not yet existing, it will be created
     *
     * @param string $key
     *            The key of the property to be changed
     * @param string $value
     *            The value to be set for the property
     * @return void
     */
    public abstract function setProperty($key, $value);

    /**
     * Removes a property from the corresponding Configuration file if it exists
     *
     * @param string $key
     *            The key of the property to be removed
     * @return void
     */
    public abstract function removeProperty($key);

    /**
     * Sanitizes a value to escape apostrophes and encapsulated in ' if the $value is a string.
     * @param string $value
     * @return string
     */
    protected function escapeValue($value)
    {
        return var_export($value, true);
    }

    /**
     * Encode a string to be escape e.g.
     * 'O\'neal' to O'neal
     *
     * @param string $value
     * @return mixed
     * @throws    \Exception    If the type of the $value cannot be determined properly
     */
    protected function parseValue($value)
    {
        if ($value == null) return null;
        $value = trim($value);
        // in case the string is enclosed with "
        if ($value [0] === "\"" && $value [strlen($value) - 1] === "\"") {
            $value = trim($value, "\"");
            return stripslashes($value);
        }
        // in case the string is enclosed with '
        if ($value [0] === "'" && $value [strlen($value) - 1] === "'") {
            $value = trim($value, "'");
            return stripslashes($value);
        }

        switch ($value) {
            case "false" :
                return false;
            case "true" :
                return true;
            case ((string)intval($value)) :
                return intval($value);
            case ((string)floatval($value)) :
                return floatval($value);
        }

        return $value;
    }
}