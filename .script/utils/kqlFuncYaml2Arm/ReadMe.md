# Run kqlFuncYaml2ArmOnForkedRepo.ps1 script

## Overview

Each pull request that updates ASimDns, ASimNetworkSession, or ASimWebSession parsers should update the deployable ARM templates accordingly.
The script 'kqlFuncYaml2Arm.ps1' generates deployable ARM templates based on ASim parsers YAML files and pushes them to the pull request branch.
For pull request from internal branches- the github action 'convertKqlFunctionYamlToArmTemplate' runs the script 'kqlFuncYaml2Arm.ps1' for each update.
For pull request from forked branches- the github action have no permissions to change the forked repo, so the script should be run manually by the forked repo owner. The github action will fail when the yaml files are not aligned with the deployable ARM templates. Running the script 'kqlFuncYaml2ArmOnForkedRepo.ps1', will generate the aligned ARM templates and the github action should succeed once the ARM templates are aligned.

## Pre-requisites

1. Powershell 7
   https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell?view=powershell-7.3
2. Python 3.6+
   https://www.python.org/downloads/
3. Yaml package for Python
    Run command - `pip install pyyaml`

## How to run the script?

1. Checkout the pull request's branch
1. Make sure there are no uncommitted changes in your local github environment.
3. Open Powershell 7 and go to your github repo base folder.
4. Run command  `.\.script\utils\kqlFuncYaml2Arm\kqlFuncYaml2ArmOnForkedRepo.ps1`
