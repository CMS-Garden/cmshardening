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


use \php\core\Autoloader;

define('ROOT_PATH', dirname(dirname(__FILE__)) . DIRECTORY_SEPARATOR);
define('CORE_PATH', ROOT_PATH . 'core' . DIRECTORY_SEPARATOR);
define('CONFIG_PATH', ROOT_PATH . 'configuration' . DIRECTORY_SEPARATOR);
define('TEST_PATH', ROOT_PATH . 'tests' . DIRECTORY_SEPARATOR);
define('VENDOR_PATH', ROOT_PATH . 'vendor' . DIRECTORY_SEPARATOR);
define('MODULES_PATH', ROOT_PATH . 'modules' . DIRECTORY_SEPARATOR);

// check php version to be at least 5.6
if (version_compare(PHP_VERSION, '5.6') < 0) {
    die("This script requires at least PHP5.6, you are using version " . phpversion());
    /*
     * currently the following known issues exist when running with PHP5.5:
     * - php\core\Util.php -> ...$segments is not supported. Instead use func_get_args() (see http://php.net/manual/en/functions.arguments.php#functions.variable-arg-list.new)
     * - php\io\i18n.php -> PHP5.5 seem to not support string concatenation in class variable definitions (line 12)
     * - When running and waiting at a point where a path has to be entered (at least under cygwin with PHP 5.5.35) an endless output of the prompt will occur after some seconds
     */
}
require_once CORE_PATH . 'Autoloader.php';

$autoloader = new Autoloader('php');
$autoloader->register();


/**
 * configure i18n
 */
$language = \php\core\configuration\Configuration::getInstance()->getProperty("Dialog.Language");
if (empty($language)) $language = 'en';
$i18n = php\io\i18n::getInstance(ROOT_PATH . 'lang/lang_%LANG%.ini', ROOT_PATH . 'lang/langcache/', $language);
$i18n->initialize();
/*
 * Usage: echo L::<section>_<Name>(<optional vprintf arg>);
 * example: echo L::Parser_PropertyRemoved(Util::now()) 
 */

// Trying to set the timezone of the server as the default time zone
// TODO: Implement variable timezone via configuration file 
date_default_timezone_set(@date_default_timezone_get());

// Stop execution if the application is not started in a CLI
if (!\php\core\Util::isCLI()) {
    die(\L::Global_NotCLI);
} else {
    // Set process title if possible
    @cli_set_process_title('BSI.CMS.2');
}


// Registers handler for system signals like SIGTERM and SIGKILL
// This only supports POSIX compatible CLIs
// Hence Windows is not supported
declare(ticks = 1);
if (function_exists("pcntl_signal")) {
    pcntl_signal(SIGTERM, array('php\core\configuration\Configuration', 'handleSig'));
    pcntl_signal(SIGINT, array('php\core\configuration\Configuration', 'handleSig'));
}