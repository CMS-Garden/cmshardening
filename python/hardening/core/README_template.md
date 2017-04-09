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
%s
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

%s

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

%s

# Miscellaneous Information

## Backups

For all automatically changed files the script will create backup files in the backup folder, which can be configured using the `Backup/BaseDir` property. Inside the backup directory, a new folder with the name `<timestamp>` will be created. For all files in this directory, subdirectories will be created in a way that they match to the original directories on the local system. The original filenames will be maintained.

## Log files

If you specify the `--log` parameter, a log documenting the changes applied to the system is created. If you specify a filename as option to this parameter, the log will be saved to that file. Otherwise, the log will be written to `stdout`.
