# Run runAsimTestersOnForkedRepo.ps1 script

## Overview

Each pull request that updates ASimDns, ASimNetworkSession, or ASimWebSession parsers should run validation tests on log analytics workspace.
There are 2 kinds on tests - schema tests and data tests.
For pull request from internal branches- the github action 'runAsimSchemaAndDataTesters' runs the tests for each update.
For pull request from forked branches- the github action have no permissions to run the tests on the forked repo, so the tests should be run manually by the code owners before they approve the pull request.

## Pre-requisites

1. Powershell 7
   https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell?view=powershell-7.3

## How to run the script?

1. Make sure that there are no uncommitted changes in your local github environment.
2. Open Powershell 7 and go to your github repository base folder.
3. Go to the pull request, get the fork and the branch from the subtitle.
The format of the subtitle is: \<user\> wants to merge \<number of commits\> commits into Azure:master from \<fork\>:\<branch\>
3. Run command  `.\.script\tests\asimParsersTest\runAsimTestersOnForkedRepo.ps1` -fork \<fork\> -branch \<branch\>