# Tanium Solution for Microsoft Sentinel

<img src="./images/Tanium.svg" alt="Tanium" width="20%"/><br>

## Overview

Integrate Microsoft Sentinel with Tanium data and remediation.

## Help

### How do I find the correct workspace location?

1. Open the [Azure "Resource groups" page](https://portal.azure.com/#blade/HubsExtension/BrowseResourceGroups)
2. Ensure you have the correct `Subscription` selected in the subscription filter
3. Click on your target/desired resource group
4. Use the `Type` filter to filter on `API Connection`
5. Click on the desired `API Connection`
6. Click on `JSON View` (right side)
7. Observe the value of the `location` key (at the bottom)

## Developer notes

Prerequisites:

- Install powershell core `brew install --cask powershell`
- (in powershell) install powershell-yaml `Install-Module powershell-yaml`
- Install make `brew install make`
- Install arm-ttk in powershell: https://github.com/Azure/arm-ttk

Ensure that you add arm-ttk to your powershell profile e.g.

```
(in powershell)

> New-Item -Type File -Path $PROFILE -Force
> vim $PROFILE

(in that file add:)

Import-Module /full/path/to/import/module/for/arm-ttk
```

Building a solution:

1. Clone the https://github.com/Tanium/Azure-Sentinel repo
2. `cd` into the repo
3. Run the build script
   ```
   ./Solutions/Tanium/build_solution.sh
   ```

The Tanium solution manifest is located within `./Solutions/Tanium/Data/Solution_Tanium.json`

Checking a solution:

1. Run the check build script
   ```
   ./Solutions/Tanium/check_build.sh
   ```

