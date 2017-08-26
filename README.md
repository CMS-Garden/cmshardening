# hardening-scripts
The intention of these scripts is to harden specific parts of a CMS installation. The following components are supported for now:

* Content Management Systems
    * Typo3 (PHP script)
    * Joomla! (PHP script)
    * WordPress (PHP script)
    * Liferay
* Runtime Environment
    * PHP
    * Java
    * Python
* Web and Application Servers
    * Apache Web Server
    * (Tomcat Application Server)
* Databases
    * MySQL
* Operating System
    * Debian
    * SSH
    * Network

The scripts are actually two separate scripts:

* PHP script to harden PHP based CMS
* Python script to harden all other components

# User Handbook

For a detailed manual (english & german) please refer to: http://www.cms-garden.org/de/projekte/cmshardening-script

## Required packages

### Debian

* *`python-yaml`* resp. *`python3-yaml`* depending on which version of python you are using*
* *`python-netifaces`* resp. *`python3-netifaces`* depending on which version of python you are using*
* *`python-six`* resp. *`python3-six`* depending on which version of python you are using*
* *`python-lxml`* resp. *`python3-lxml`* depending on which version of python you are using*

```
$ sudo apt-get install python python-yaml python-netifaces python-six
```

or

```
$ sudo apt-get install python3 python3-yaml python3-netifaces python3-six
```

## Recommended packages

* *`coloredlogs`* for displaying colored logs on the console

## Quick start
The scripts are implemented in a way that they are executable without prior configuration. Missing settings are prompted for.
### Hardening of PHP-based Content Management Systems

`cd` into directory `php` and run
```
$ php index.php
```  
For more details on this script see the [User Handbook for the PHP script](php/README.md)

### Hardening of everything else

`cd` into directory `python` and run
```
$ sudo ./hardening.sh
```
For more details on this script see the [User Handbook for the Python script](python/README.md)

# Licensing
## License of the hardening scripts
These scripts are licensed under GNU GPLv3. However, these scripts are bundled with libraries or components licensed various licenses.
## Licensing of components
| Component | Version | License | License URL | Usage | Source |
|-|-|-|-|-|-|
| Python | 2.7 | Python 2.7 License | https://www.python.org/download/releases/2.7/license/ | Interpreter for Python scripts | |
| Python | 3.5 | PSF LICENSE AGREEMENT FOR PYTHON 3.5.1 | https://docs.python.org/3/license.html | Interpreter for Python scripts | |
| PyYAML | 3.11 | The MIT License | https://opensource.org/licenses/MIT | Parsing of YAML files in Python scripts | |
| PHP | 5.6 | PHP License v3.01	| http://www.php.net/license/3_01.txt | Interpreter for PHP scripts | |
| spyc | | The MIT License | https://opensource.org/licenses/MIT | Parsing of YAML files in PHP scripts | https://github.com/mustangostang/spyc/ |
| TYPO3 | 7.6.0 | GPL-2.0+ | http://www.opensource.org/licenses/gpl-license.php | Parsing of TYPO3 configuration | https://typo3.org/download/ |
