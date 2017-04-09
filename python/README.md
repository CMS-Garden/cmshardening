omitting __init__
omitting __init__
ApacheConfig has no keyword method
Group has no keyword method
JavaConfig has no keyword method
NetworkConfiguration has no keyword method
OSInfo has no keyword method
PackageManager has no keyword method
Passwd has no keyword method
PHPConfig has no keyword method
PythonConfig has no keyword method
# Python hardening script

A [python](https://www.python.org/) based script was implemented to harden the
configuration of components required to manage and run a content management
system in a Shared-Hosting Environment, where a user usually does only have a
restricted shell access.

Currently, the following components are supported:

* Operating system: **Debian Linux**
* Firewall rules: **iptables**
* Web server: **Apache 2**
* Remote Management: **OpenSSH**
* Programming language/Scripting environment: **php**, **python**, **java**
* Database management system: **MySQL**
* Content Management System: **Liferay CE**, **Plone**

## Requirements

To run the script, the following python package need to be installed:

* yaml
* netifaces
* six
* lxml
* psutil

We suggest that you use the package manager of your distribution to install the
required packages. In Debian Linux, the packages are named python-*&lt;package name&gt;* resp. `python3-<package name>`; depending on which version of python you are using. E.g., you could install all requirements using the command

```bash
$ sudo apt-get install python3{,-{yaml,netifaces,six,lxml}}
```

The script can only be run from command line for now. It can be extended to
support running as Web application.

You **MUST** run this script as non-privileged user, and you **MUST** use `sudo` to do this. This is required because we need root privileges to modify any configuration files; and we disable root logins in your sshd configuration. To prevent you from locking out of our own system, we add the name of your currently logged in user to the sshd configuration as a user which is allowed to login using ssh.

## Recommended packages

We recommend installing *`coloredlogs`* if you like to have colored logs on the console.

# Running this script

## Quick start

`cd` into directory `python` and run
```
$ sudo python hardening.py
```

## Usage

```
$ python hardening.py --help
usage: hardening.py [-h] [--mode {interactive,diff,silent,checkonly}] [--log [logfile]]
                    [--lang {en_US,de_DE}] [--version] [--documentation]

optional arguments:
  -h, --help            show this help message and exit
  --mode {interactive,diff,silent,checkonly}
                        select mode in which this script will run
  --log [logfile]       display a log of applied changes; use can use '-' as
                        filename to log to stdout
  --lang {en_US,de_DE}  select display language               
  --version             display version
  --documentation       display full documentation in markdown format

```

## Workflow of the Script

1. The script introduces the user with some information to inform about risks and usage of the script
1. If the selected `mode` is not `silent`, a menu is displayed which enables the user to select modules to be run
1. There might be some certain general information the user has to enter. (For example which of the network interfaces shall be used for management access)
1. Now the actual hardening takes place. For each so called Util the user will be informed about the action that will be performed. If the interactive mode (`--mode=ask`) is enabled the user will be prompted to confirm each change.
1. All hardening steps are performed on temporary files first and will be committed to the original files as soon as all changes are accomplished.
  If difference mode (`--mode=diff`) is enabled, the user will be prompted to confirm the sum of all changes to a file
1. For each file to be adjusted the script creates a backup file (the destination can be configured using the global `Backup.Basedir`-property)

  Currently, no rollback is possible, all directly changed configuration files are copied to the backup directory, while maintaining the original folder structure. You can copy those files back, if you need too. Be aware that some hardening steps require the execution of system commands (such as `usermod` or `a2enmod`), which cannot be rolled back by copying some files

1. After a short notification about the backups folder, the script exits.

# Configuration

All configuration files use the [YAML](https://en.wikipedia.org/wiki/YAML) syntax, with the following extensions:

* property values are interpolated (see Interpolation)
* references (\*) can refer to anchors (&) in different files. All YAML files are merged before references are resolved by the YAML parser.

The configuration of this toolset is separated into multiple files:

|Filename | Description
|---------|------------
|`config.yml` | Global Configuration file for the whole toolset
|`modules/`*`<mycomponent>`*`.yml` | Configuration file used for the component *`<mycomponent>`*. For example, the configuration for hardening sshd is stored in `modules/sshd.yml`

## Interpolation

Interpolation is a features which replaces a certain part of a string (substring) by some other string, using the following rules:

* if the substring starts with `info:`, then Interpolation starts by

  1. detecting the interpolated substring
  1. replacing the interpolated substring by its value

* interpolation is run *once by string*, for all matching substrings of a string.

### Detection of the interpolated substrings

Every interpolated substring consists of parts, which are alphanumeric values and are separated by colon (:). For example, if the substrings `info:example:group` and ` info:example:mark` interpolate to `world`and `!`, resp.; the string

```
"hello, info:example:group info:example:mark"
```

is interpolated to

```
"hello, world !"
```

### Replacement of interpolated substrings

|Substring| Replacement
|-|-
| `info:apache:apache_config` | returns the absolute path of the local `apache2.conf` file          Normally, the path should be `/etc/apache2/apache2.conf` in Debian Linux
| `info:apache:security_config` | returns the absolute path of the local `security.conf` file          Normally, the path should be `/etc/apache2/conf-available/security.conf` in Debian Linux
| `info:apache:ssl_config` | returns the absolute path of the local `ssl_config` file          Normally, the path should be `/etc/apache2/mods-available/ssl_config` in Debian Linux
| `info:condition:false` | evaluates to `False`
| `info:condition:hardening_for_joomla` | returns `True` if the configuration must be tailored for Joomla
| `info:condition:hardening_for_liferay` | returns `True` if the configuration must be tailored for Liferay
| `info:condition:hardening_for_plone` | returns `True` if the configuration must be tailored for Plone
| `info:condition:hardening_for_typo3` | returns `True` if the configuration must be tailored for Typo3
| `info:condition:hardening_for_wordpress` | returns `True` if the configuration must be tailored for Wordpress
| `info:condition:has_apache_installed` | returns `True` if Apache (apache2) is installed
| `info:condition:has_network_interface:<index>` | returns `True` if a specific interface exists.          All network interfaces are internally indexed, starting with `0`; the interfaces `lo` is omitted. So, the first         interfaces may be externally reachable has the index `0`
| `info:condition:has_package_installed:<package>` | returns `True` if `package` is installed on the local system
| `info:condition:has_php_installed` | returns `True` if PHP (php-fpm) is installed
| `info:condition:true` | evaluates to `True`
| `info:env:<var_name>` | interpolates the given environment variable
| `info:net:default_gw` | returns the IP address of the default gateway
| `info:net:gateway:<index>` | returns the gateway ip address of the interface with the given `index`
| `info:net:inet_address:<index>` | returns the ip address of the interface with the given `index`
| `info:net:interface:<index>` | returns the name of the interface with the given `index`
| `info:net:interface_info:<index>:<infoname>` | returns some specific information of the interface with the given `index`          Supported values for `infoname` are `addr`, `netmask` and `peer`
| `info:net:interfaces` | returns the names of all network interfaces (excluding `lo`)
| `info:net:management_address` | returns the IP address which shall be used by management services, such as SSH
| `info:net:nameservers` | returns a list of ip addresses, representing name servers
| `info:net:netmask:<index>` | returns the subnet mask of the interface with the given `index`
| `info:net:public_address` | returns the IP address which shall be used by services which are publicly available
| `info:net:resolv_conf` | returns the current DNS configuration
| `info:net:static_addresses` | returns a list of all ip addresses (excluding `127.0.0.1`)
| `info:php:php_ini` | returns the absolute path of the global php configuration file.          Currently, we simply return `/etc/php5/fpm/php.ini`
| `info:resolve_key:<keyname>` | Uses entries in `config.yml` to interpolate.          Each `keyname` is mapped to an associative list, where the key is a regular expression that is matched against         the result of OSInfo::distribution_name(). If the distribution name matches the given regular expression, then         the interpolated string is replaced by the value of the associative list from `config.yml`
| `info:user:logname` | returns the name with which the user has logged in to the current system.          This is normally your current username. But: If you used `sudo` to become another user, then this interpolates         to your username you had *before* you invoked `sudo`

## Global Configuration

Example:

```yaml
Logging:
    LogLevel: DEBUG
    LogHandler: StreamHandler
    Verbose: True

RunModules: [network, apache, sshd, php, WordPress, debian, java, python]

Backup:
  BaseDir: "$HOME/hardening-backup"

HardeningSettings:   {

    ssh-runtime-user: &ssh-runtime-user         "sshd",
    ssh-runtime-group: &ssh-runtime-group       "ssh",
    ssh-listening-port: &ssh-listening-port     "22"
}
```

|Setting|Description
|-|-
|`Logging/LogLevel`| specifies how verbose the toolset shall be. Valid values (with increasing verbosity) are `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`
|`Logging/LogHandler`| Name of a class from package `logging.handlers`. Valid values are `StreamHandler`, `FileHandler` or `NullHandler`
|`RunModules`| a list of modules which shall be run. Each entry in this list refers to a YAML file int the `modules` directory.
|`Backup/BaseDir`| Name of the directory where backup files will be stored
|`HardeningSettings`| Here, a lot of global settings can be specified, so that it is not necessary anymore to edit any YAML files. All settings here should be marked with an anchor (&).

## Hardening Modules

The configuration of any module is divided into two parts:

* `RunSections` contains a list of sections names. For each entry in this list there should be a *Section* in the next part of the module
* Each *Section* is a associative array with the following content:
  * `RunUtils` contains a list of associative array, each of which names a class from the `utils` package and contains options. For every entry in list list, an instance of the specified class is being created, using the options specified
  * `Options` is an associative array which contains options that have to be applied for every `RunUtils`-entry.

## Utils

|util class| option |is required?|meaning
|-|-|-|-
|`utils.HardeningUtil`| | |   |
|`apache.ApacheDismod`| | | this module runs a2dismod to disable an apache module |
| | `modname` | True | name of the apache module to be disabled
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`apache.ApacheEnmod`| | | this module runs a2enmod to enable an apache module |
| | `modname` | True | name of the apache module to be enabled
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`configfile.ApacheConfigEntry`| | | ApacheConfigEntry is a specialized version of ConfigFileEntry which is able to find a specific section inside the config file and put the requested value into this section |
| | `transaction` | True | path of the apache config file
| | `key` | True | name of the configuration setting
| | `value` | True | value to be set for the configuration setting
| | `section` | False | section inside the config file where setting must be placed in
| | `listseparator` | False | if the value is a list then this options specifies how the distinct values must be separated
| | `separator` | False | the string that divides setting name and setting value in the config file
| | `commentchar` | False | all characters in a line after the comment character are ignored
| | `multiple` | False | if this is set to true then existing settings with the same key and different value are not overwritten, but a new line is being inserted
| | `before-key` | False | describes a key in the config file BEFORE which the current setting will be inserted.
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`configfile.ConfigFileEntry`| | | searches through the given configuration file if there already exists a setting whose name matches that of the given key. If a matching entry is found, it is being updated. If no matching entry is found, the setting will be appended to the file. If the user has set `multiple` to `True`, than also the value will be used to find a matching value. This allows to add multiple settings with the same key, but different value, to a file. |
| | `transaction` | True | path of the config file
| | `key` | True | name of the configuration setting
| | `value` | True | value to be set for the configuration setting
| | `separator` | False | the string that divides setting name and setting value in the config file
| | `listseparator` | False | if the value is a list then this options specifies how the distinct values must be separated
| | `commentchar` | False | all characters in a line after the comment character are ignored
| | `multiple` | False | if this is set to true then existing settings with the same key and different value are not overwritten, but a new line is being inserted
| | `before-key` | False | describes a key in the config file BEFORE which the current setting will be inserted.
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`configfile.ConfigLine`| | |   |
|`configfile.IniFileEntry`| | |   |
| | `transaction` | True | path of the apache config file
| | `key` | True | name of the configuration setting
| | `value` | True | value to be set for the configuration setting
| | `section` | False | section inside the config file where setting must be placed in
| | `listseparator` | False | if the value is a list then this options specifies how the distinct values must be separated
| | `separator` | False | the string that divides setting name and setting value in the config file
| | `commentchar` | False | all characters in a line after the comment character are ignored
| | `multiple` | False | if this is set to true then existing settings with the same key and different value are not overwritten, but a new line is being inserted
| | `before-key` | False | describes a key in the config file BEFORE which the current setting will be inserted.
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`configfile.XmlFileEntry`| | |   |
| | `transaction` | True | path of the config file
| | `xslt` | True | XML transform to be applied to the configuration file
| | `xmlns` | False | default XML namespace used in the file
| | `namespace-prefix` | False | XML namespace prefix used in the file
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`filesystem.ChangeOwner`| | | this class can be used to change the owner (and, if necessary, the owning group) of a file |
| | `user` | True | name of the new owner
| | `group` | False | name of the owning group
| | `recursive` | False | additional parameter for ChangeOwner
| | `apply-to-files` | False | 
| | `apply-to-directories` | False | 
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`filesystem.ChangePermissions`| | | this class can be used to change the access permissions of a file. The mode must be a valid octal number between `000` and `777`. |
| | `mode` | True | mode to be used as new access permissions
| | `recursive` | False | additional parameter for ChangeOwner
| | `apply-to-files` | False | 
| | `apply-to-directories` | False | 
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`filesystem.DeleteFile`| | | this class can be used to delete a file from the filesystem. wildcards for filenames are currently not supported |
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`filesystem.Directory`| | | creates a directory |
| | `path` | True | complete path of the new directory
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`module.EnterModule`| | |   |
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`net.Firewall`| | | creates a firewall rule. Be aware that the default policy for all chains is "DROP", which cannot be altered using configuration files |
| | `protocol` | True | name of the protocol. must be either `tcp`, `udp` or `icmp`
| | `src` | False | name or ip address of the sending host
| | `dst` | False | name of ip address of the receiving host
| | `action` | False | specifies what shoud be done with matching packets. Default value is `ACCEPT`
| | `chain` | False | name of the chain where the rule must be inserted. Should be `INPUT`, `OUTPUT` or `FORWARD`
| | `srcport` | False | source port of the packet. Only valid for `tcp` and `udp`
| | `dstport` | False | destination port of the packet. Only valid for `tcp` and `udp`
| | `icmp-type` | False | ICMP type. Please run `iptables -p icmp -h` to see which values are supported on your system
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`net.StaticIP`| | | uses the current network configuration, no matter if its being configured statically or dynamically, and writes a network configuration file, so that the current configuration is static from now on. No dhcp will be used afterwards |
| | `interface` | True | name of the interface to be configured
| | `inet-address` | True | IPv4 network address
| | `netmask` | False | subnet mask, defaults to 255.255.255.0
| | `gateway` | False | IPv4 address of the default gateay, if any
| | `dns-nameservers` | False | IPv4 addresses of DNS name servers
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`os.CheckVersion`| | | compares the version of an installed component with a version that is specified as parameter |
| | `key` | True | specifies which version you are interested in. must be one of `php`, `java` or `python`
| | `version` | True | specifies a version with which the installed version should be compared
| | `operation` | True | must be `greater_then`
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`os.ConfigureService`| | | this class is used to enable, disable, start or stop a service |
| | `servicename` | True | unique name of the service
| | `action` | True | specifies what must be done with the service. must be one of `enable`, `disable`, `start` or `stop`
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run
|`os.UserItem`| | | creates a user. If the user already exists, it will be modified. Be aware: this class does not use Transactions, so there is no rollback possible. |
| | `name` | True | name of the user to be created
| | `home` | False | home directory
| | `shell` | False | login shell
| | `meta` | False | contains information about that specific hardening step
| | `run-if` | False | specifies under which condition this util will be run

# Miscellaneous Information

## Backups

For all automatically changed files the script will create backup files in the backup folder, which can be configured using the `Backup/BaseDir` property. Inside the backup directory, a new folder with the name `<timestamp>` will be created. For all files in this directory, subdirectories will be created in a way that they match to the original directories on the local system. The original filenames will be maintained.

## Log files

If you specify the `--log` parameter, a log documenting the changes applied to the system is created. If you specify a filename as option to this parameter, the log will be saved to that file. Otherwise, the log will be written to `stdout`.

