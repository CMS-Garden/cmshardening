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

/**
 * Class Autoloader
 * This class loads all files needed to call a referenced class based on the namespace and the class name
 * Thus it is necessary use correct folder names according to the namespaces and file names according to the class names.
 * @package php\core
 */
class Autoloader
{
    private $namespace;

    public function __construct($namespace = null)
    {
        $this->namespace = $namespace;
    }

    public function register()
    {
        spl_autoload_register(array($this, 'loadClass'));
    }

    public function loadClass($className)
    {
        if ($this->namespace !== null) {
            $className = str_replace($this->namespace . '\\', '', $className);
        }

        $className = str_replace('\\', DIRECTORY_SEPARATOR, $className);

        $file = ROOT_PATH . $className . '.php';

        if (file_exists($file)) {
            require_once $file;
        }
    }
}
?>