# PHP Hardening Script
A php based hardening script was implemented to explicitly harden PHP based CMS in a shared-hosting Environment, where a user usually does only have a restricted shell access. Thus only the following CMS are supported for now:

* Joomla!
* Typo3
* WordPress

## Requirements

The script requires PHP to be installed. Further Extensions like 'runkit' are optional.

The script can only be run from command line for now. It can be extended to support running as Web application.

It is recommended to run the execute the script with a non-privileged user, whereby the it might be possible that the runtime user is not allowed to access all files needed to be changed, deleted or created. In this case the script will inform the user.

## Running the Script
### Quick start
`cd` into directory `php` and run

    $ php index.php

### Usage

    $ php index.php --help
    This hardening script intends to configure certain Content Management Systems (CMS) to improve the security.
    The following parameters are available:
     -h | --help        This help message
     -c | --checkOnly   Run the script without making any changes
     -i | --interactive Before making any changes the user is asked to confirm
     -s | --silent      Print changes but dont ask the user to confirm
     -l | --lang        Changes the language of the script output to 'en' or 'de'. (requires the PHP Extension 'classkit' or 'runkit')
     This parametrisation can also be done in the config.yml file. The above script arguments will temporarily override the configuration.

### Workflow of the Script
1. The script introduces the user with some information to inform about risks and usage of the script
2. There might be some certain general information the user has to enter. (For example if the server supports SSL/TLS)
3. A selection menu is provided to choose the CMS to be hardened
4. The script now needs to know where to find the CMS installation and some other details to harden the CMS. All this data is prompted for in this step.
5. For each file to be adjusted the script creates a backup file (usually located in the `backups` folder)
6. Now the actual hardening takes place. For each so called Util the user will be informed about the action that will be performed. If the interactive mode (`Dialog.interactive=true` in `config.yml`) is enabled (which is by default) the user will be prompted to confirm each change.
7. As there are Hardening guidelines that cannot be implemented with automatic hardening, these steps will be displayed in form of a checklist, to advise the user to manually perform certain actions.
7. After after all these hardening steps the user is asked to check the system. At this point the user can choose to roll back all changes to recover the original state.
8. After a short notification about the `backups` folder, the script exits.

## Configuration
The configuration is separated into two parts:

* General Configuration in `config.yml`  
For general settings of the script
* Module Configuration in `modules/<module>.yml`  
For module specific settings

The configuration files are in YAML format to enable a complex and nested specification.

In case the configuration is incomplete the user will be prompted to enter the missing value during the script execution.

### General Configuration
The content of the `config.yml` contains several settings to customize the script execution.
The most important settings here are:

* `Dialog.Language` to choose the language of the script. Possible values are `de` and `en`. Alternatively one can append the command line argument `--lang`.
* `HardeningSettings.CheckOnly` to specify if the script should without actually making any changes. Possible values are `true` and `false`. Alternatively one can append the command line argument `--dryrun` or `--checkonly`

### Module Configuration
For each module that is defined in the General Configuration (`config.yml`) in the list `Hardening.IncludeModules` the appropriate YAML file is loaded as well from the `modules` folder.
In these configuration files specific settings for this module are described.
Besides configuration settings for the location of the CMS, there is also defined what should be done to harden the CMS. So if you wish to not enter the path to the CMS location each time you run the script, you can store the path in the module configuration file instead.
Usually the user does not need to change any of the harden options. Nevertheless it is possible to alter the values of CMS configuration settings very easily. Additionally one can add hardening options of the same kind without the need to implement code.

### Utils

|util class| option |is required?|meaning
|-|-|-|-
|`utils.UtilObject`| | | |
|`config.JoomlaConfigFileEntry`| | | Writes an key-value-pair into a Joomla-Config-File. |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.
| | `key` | True | name of the configuration setting.
| | `value` | True | value to be set for the configuration setting.
| | `run-if` | False | specifies under which condition this util will be run
|`config.LocalPHPConfigFileEntry`| | | Writes an key-value-pair into the local PHP-Config-File. |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.
| | `key` | True | name of the configuration setting.
| | `value` | True | value to be set for the configuration setting.
| | `run-if` | False | specifies under which condition this util will be run
|`config.Typo3ConfigFileEntry`| | | Writes an key-value-pair into a Typo3-Config-File. |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.
| | `key` | True | name of the configuration setting.
| | `value` | True | value to be set for the configuration setting.
| | `run-if` | False | specifies under which condition this util will be run
|`config.WordpressConfigFileEntry`| | | Writes an key-value-pair into a Wordpress-Config-File. |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.
| | `key` | True | name of the configuration setting.
| | `value` | True | value to be set for the configuration setting.
| | `run-if` | False | specifies under which condition this util will be run
|`filesystem.DeleteFile`| | |  Backup and remove a file (with the ability to rollback the backup-file). |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.
| | `value` | True | the file to delete.
|`filesystem.DeleteTypo3ConfigFile`| | |  Deletes a Typo3ConfigFile which is located within the ConfigurationFolder. |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.
| | `value` | True | the file to delete.
|`meta.Description`| | | Print a description. Used for hardening steps which can not be done automatically. |
| | `name` | True | title of the hardening step.
| | `description` | True | description of the hardening step.

## Miscellaneous Information
### Backups
For all automatically changed files the script will create backup files in the `backups/` folder. The filename of the backup file contains the original file name and a time stamp. Hardening steps the user has to do manually will not be backed up.

### Log files
For all that is done in the script log entries are created and written to log files. This enable to afterwards reconstruct the script run. Each run of the script will create a new log file (including a time stamp in the file name) located in the `logs/` folder.

### Languages
For now there are two languages supported: German (`de`), English (`en`)
These can be configured in the [config.yml] (config.yml) or temporarily with the command line argument `--lang=xx` or `-l xx`
Further languages could be created by maintaining the files located in the `lang/` folder

### File Access
The script will access certain files in certain ways:

| File/Folder | Access | Description |
|-|-|-|
| `php/` | read | The script of course needs to read all the script files
| `php/backups/` | write | The script will create backup files. If this folder does not exist, the script will create it with proper file permissions.
| `php/logs/` | write | The script will create log files. If this folder does not exist, the script will create it with proper file permissions.
| `php/lang/langcache/` | read/write | The script needs to write the language cache files to enable translation.  If this folder does not exist, the script will create it with proper file permissions.
| `$WordPress/wp-config.php` | read/write | To harden the WordPress configuration
| `$TYPO3/typo3conf/LocalConfiguration.php` | read/write | To harden the TYPO3 configuration
| `$JOOMLA/configuration.php` | read/write | To harden the Joomla! configuration
| `$TYPO3/ENABLE_INSTALL_TOOL` | delete | To delete the marker for enabling the install tool

This list might not be complete as some hardening modules could be extended in the future to e.g. delete more unnecessary files. Placeholder like $JOOMLA describe the root folder of the CMS, which the user provides.
