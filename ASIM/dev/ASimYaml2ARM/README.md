# Using KqlFuncYaml2Arm.py

The KqlFuncYaml2Arm script generated deployable ARM templates from KQL function YAML files.

## Installing

To use:

- Download all the files in this directory to a folder.
- Download and install the latest Python 3 for your platform, for example from [here](https://www.python.org/downloads/). This script was tested on Windows.
- Optionally enable the script to run as a command. This document assumes you performed this. On Windows do the following:
    - Install the requirements.
        - python -m pip install -r requirements.txt
    - Add the folder to downloaded the files to to your system path.
    - Add `.py` to your system PATHEXT system variable
    - Run the following commands:

```
assoc .py=Python.File
ftype Python.File=<full path of the python executable> "%1" %*
```

## Using

### Usage

```
KqlFuncYaml2Arm
    [-h] 
    [-m package, file, asim or asimdev] 
    [-d destination folder] 
    [-t templates folder] 
    [-b branch]
    [-u uri] 
    [-l debug]
    [files and folders ...]
```

### Arguments

**files and folders**: List of YAML files and folders to process. For folders, each YAML file in the folder will be converted.

Optional arguments:

| Parameters | Description |
| ---------------------------- | ----------- |
| -h, --help | Show a help message and exit |
| -m, --mode | Select the mode:<br> - "files" to translate each input YAML files to an ARM template.<br> - "package" to create a full deployment package including readme files and a full deployment template.<br> -"asim" to create a full package using ASIM specific templates.<br> -"asimdev" is simliar to `asim` but does not use `aka.ms` links.<br><br> Defaults to "files". | 
| -d, --dest | The output folder. Defaults to the ARM subdirectory of the current working directory. |
| -t,--templates | The path of the templates for ARM templates and readme files. Defaults to the script directory. |
| -b, --branch | For `asim` and `asimdev` modes, the ARM templates links in the full deployment and readme files point to this github branch. The Github repository itself is embedded in the template files. Defaults to "master". |
| -u, --uri | For package mode, the based uri under which the package will be available. Used to generate the full deployment and readme files. If using package mode, this field is mandatory and has no default. |
| l, --loglevel | Specify the logging level.Defaults to warning. Supported values are: `critical`, `error`, `warning`, `info`, and `debug`. |
|||

### Examples

To convert a single file, and keep the resuling template in the same directory, change the working directory to the folder in which the file resides and use

``` cmd
cd <folder in which the file resides>
KqlFuncYaml2Arm <filename.yaml>
```

To generate a standard ASIM schema parser package, assuming ASIM GitHub folder structure:

```cmd
cd <the location of your GitHub repose>\GitHub\Azure-Sentinel\Parsers\ASimProcessEvent
KqlFuncYaml2Arm -m asim -d ARM Parsers
```

## About modes

The script has three modes:

- In the default `files` mode, each input file (or YAML files in a folder), is converted as a corresponding json ARM template is created in the destination folder.
- In `package` mode, a full deployment package is generated:
  - Each input file is converted and stored in a sub-folder of the destination folder along side a README file. By default, the README file includes a button for one click deployment of the ARM template.
  - A full deployment template that will deploy all functions is created in the destination directory.
  - A README file for the package is created in the destination directory. By default the README file includes a button for one click deployment of the package.
  
  The mandatory `uri` parameter is used by the default README and deployment templates as the location from which the package is intended to be available, enabling the nested ARM template and one click deployment buttons.

- The `asim` mode is similar to the `package` mode, but the default README and deployment templates are geared towards an ASIM deployment from the Microsoft Sentinel GitHub. The `uri` is not provided as a parameter, but is rather embedded in the templates. the `branch` parameter can be used to control the branch that the package is intended ot be deployed from, especially for testing prior to merging to `master`.

- The `asimdev` mode is similar to `asim` but uses an alternative set of templates that generate a full link rather than a shorthand `aka.ms` link. The latter will usually point to the `master` branch, and may not be available when developing.

## <a name="templates"></a> About templates

The README files and ARM templates are generated from a template, that can include values from the YAML files. There are sets of templates for each non-files mode: `asim`, 'asimdev', and `package`. The default templates are included with the script and should be located in the script folder. You can customize the templates in-place, or by copying to another folder and using the `-t` parameter to point the script to this folder for templates.

The templates support placeholders that are replaced with the relevant values when the target files are created. Those are (all in lowercase):

- **filename**: The name (without folder) of the file converted.
- Script parameters: 
  - **branch**: The branch provided as parameter to the script.
  - **uri***: The uri provided as parameter to the script. Note that to README files, this value is provided after URL encoding.
- YAML file values:
  - **product**
  - **title**
  - **description**

The templates are:

| Template | Description | Supported placeholders |
| -------- | ----------- | ---------------------- |
| asim_readme.md<br>asimdev_readme.md<br>package_readme.md | The template for the package README.md file. | branch (encoded)<br>schema<br>uri (encoded) |
| asim_func_readme.md<br>asimdev_func_readme.md<br>package_func_readme.md | The template for the function specific README.md file | branch&nbsp;(encoded)<br>description<br>filename<br>product<br>schema<br>title<br>uri (encoded) |
| asim_arm_template<br>asimdev_arm_template<br>package_arm_template | The template for the package ARM template.<br><br>The resource element of this schema is duplicated for each deployed function. Only the URI part of the template requires customization and it is the only part for which placeholder replacement is supported | branch<br>filename<br>schema<br>uri |
| func_arm_template | The template for the ARM template of each function. This template usually does not require modification, and is used across all modes. | - |
||||
