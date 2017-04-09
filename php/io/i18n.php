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

use \Exception;
use php\core\Util;

/**
 * Class i18n
 * This class can handle different language files, which can be used in code by means of \L::<section>_<textProperty>
 * @package php\io
 */
class i18n
{
    private $langFile = 'lang_%LANG%.ini';
    private $langFileParsed = '';
    private $cachePath = 'langcache' . DIRECTORY_SEPARATOR;
    private $cacheFile = '';
    private $lang = 'en';
    private $sectionSeparator = '_';

    private static $instance = null;

    /**
     * Creates an instance of the i18n class (Singleton pattern)
     * @param $langFile $string the file path of the language file including the %LANG% placeholder
     * @param $cachePath string the Path of the language cache folder (including the trailing /)
     * @param $lang string the identifier of the language (en, de, etc.)
     * @return \php\io\i18n
     */
    static public function getInstance($langFile = NULL, $cachePath = NULL, $lang = NULL)
    {
        if (null === self::$instance) {
            self::$instance = new i18n($langFile, $cachePath, $lang);
        }
        return self::$instance;
    }

    private function __construct($langFile = NULL, $cachePath = NULL, $lang = NULL)
    {
        if (!Util::is_null_or_empty($langFile)) {
            $this->langFile = $langFile;
        }
        if (!Util::is_null_or_empty($cachePath)) {
            $this->cachePath = $cachePath;
        }
        if (!Util::is_null_or_empty($lang)) {
            if (!$this->validateLang($lang)) throw new Exception('The language provided is not in a proper format');
            $this->lang = $lang;
        }
    }

    public function initialize()
    {
        if (!class_exists('L') || function_exists('classkit_import') || function_exists('runkit_import'))
            // define and check the language file path
            $this->langFileParsed = str_replace('%LANG%', $this->lang, $this->langFile);
        if (!file_exists($this->langFileParsed)) {
            throw new Exception("The language file " . $this->langFileParsed . " does not exist.");
        }

        // create cachePath in filesystem if not yet exist
        if(!file_exists($this->cachePath))
            mkdir($this->cachePath, 0777, true);
        // define the actual cache file path
        $this->cacheFile = $this->cachePath . 'lang_cache_' . $this->lang . '.php';

        // parse the language file
        $parsed_ini_file = parse_ini_file($this->langFileParsed, true);

        // generate the content of the cache file by parsing the $parsed_ini_file
        $cacheConstants = $this->generateCacheConstants($parsed_ini_file);

        $cacheFileContent = "<?php class L { " . PHP_EOL .
            $cacheConstants .
            "\tpublic static function " . '__callStatic($string, $args) {' . PHP_EOL .
            "\t\t" . 'return vsprintf(constant("L::" . $string), $args);' . PHP_EOL .
            "\t}" . PHP_EOL .
            "}" . PHP_EOL;
        // write to cache file
        file_put_contents($this->cacheFile, $cacheFileContent);

        // (re)load the cache file containing the language class
        if (function_exists('runkit_import'))
            runkit_import($this->cacheFile);
        else if (function_exists('classkit_import'))
            classkit_import($this->cacheFile);
        else if (!class_exists('L'))
            include_once($this->cacheFile);
        else
            echo "WARNING: It is not possible to redefine the language settings. For this your system needs the php extension 'classkit' or 'runkit'. Instead of the parameter 'lang', please specify the proper language in the config.yml: Dialog.Language" . PHP_EOL;
    }

    private function generateCacheConstants($parsed_ini_file, $section = '')
    {
        $return = '';
        foreach ($parsed_ini_file as $key => $value) {
            if (is_array($value)) {
                $return .= $this->generateCacheConstants($value, $section . $key . $this->sectionSeparator);
            } else {
                $return .= "\tconst " . $section . $key . " = " . var_export($value, true) . ";" . PHP_EOL;
            }
        }
        return $return;
    }

    /**
     * @return null|string
     */
    public function getLangFile()
    {
        return $this->langFile;
    }

    /**
     * @param null|string $langFile
     * @return i18n
     */
    public function setLangFile($langFile)
    {
        $this->langFile = $langFile;
        return $this;
    }

    /**
     * @return null|string
     */
    public function getCachePath()
    {
        return $this->cachePath;
    }

    /**
     * @param null|string $cachePath
     * @return i18n
     */
    public function setCachePath($cachePath)
    {
        $this->cachePath = $cachePath;
        return $this;
    }

    /**
     * @return null|string
     */
    public function getLang()
    {
        return $this->lang;
    }

    /**
     * @param null|string $lang
     * @return i18n
     * @throws Exception In case the language provided is not in a proper format
     */
    public function setLang($lang)
    {
        if (!$this->validateLang($lang)) throw new Exception('The language provided is not in a proper format');
        $this->lang = $lang;
        return $this;
    }

    /**
     * @param $lang string the language string to be validated
     * @return bool true if the validation was successful
     */
    private function validateLang($lang)
    {
        if (preg_match('/^\w\w$/', $lang) === 1) return true;
        return false;
    }

}