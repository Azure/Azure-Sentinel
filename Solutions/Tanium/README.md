# Tanium Sentinel package

<img src="./images/Tanium.svg" alt="Tanium" width="20%"/><br>

## Overview

Tanium Sentinel integration packages help you import / visualize Tanium data and act on these findings from within Sentinel.

## Manual Installation for testing

### Step by step

1. Open [Tanium/Azure-Sentinel](https://github.com/Tanium/Azure-Sentinel)
2. Open the branch holding the new solution build you wish to test
1. Download the Tanium mainTemplate.json file from Solutions/Tanium/Package
2. Open the [Azure "Custom deployment" page](https://portal.azure.com/#create/Microsoft.Template)
3. Click "Build your own template in the editor"
4. Click "Load file" and upload the download mainTemplate.json file
5. Click "Save"
6. Set the following settings (leave the rest as defaults)
    - Subscription (picker)
      - Resource Group (picker)
    - Workspace-location
      - Note: this is something like `westus` not `West US`... it must match where your api connection lives [see note below](#help-workspace-location))
    - Workspace (the name of your Sentinel workspace)
    - Playbook1-Tanium Api Token
    - Playbook1-Tanium Server Hostname
    - Playbook2-Tanium Api Token
    - Playbook2-Tanium Server Hostname
    - Playbook3-Tanium Api Token
    - Playbook3-Tanium Server Hostname
    - Playbook4-Tanium Api Token
    - Playbook4-Tanium Server Hostname
    - Playbook5-Tanium Api Token
    - Playbook5-Tanium Server Hostname
    - Playbook6-Tanium Api Token
    - Playbook6-Tanium Server Hostname
    - Playbook7-Tanium Api Token
    - Playbook7-Tanium Server Hostname
7. Click `Review + create`
8. After validate click `Create`

## Help

<a name=help-workspace-location>

### How do I find the correct workspace location?

1. Open the [Azure "Resource groups" page](https://portal.azure.com/#blade/HubsExtension/BrowseResourceGroups)
2. Ensure you have the correct `Subscription` selected in the subscription filter
3. Click on your target/desired resource group
4. Use the `Type` filter to filter on `API Connection`
5. Click on the desired `API Connection`
6. Click on `JSON View` (right side)
7. Observe the value of the `location` key (at the bottom)

<a name=help-no-api-connection>

### What if I dont have an API connection?

- TODO: Walk customer through setting up connection in Logic App
- TODO: Automate this

## Developer notes

Prerequisites:

- Install power shell core `brew install --cask powershell`
- Install power shell YAML parser `Install-Module powershell-yaml`
- Install make `brew install make`

Building a solution:

1. Clone the https://github.com/Tanium/Azure-Sentinel repo
2. `cd` into the repo
3. Run the build script
   ```
   ./Solutions/Tanium/build_solution.sh
   ```

The Tanium solution manifest is located within `./Solutions/Tanium/Data/Solution_Tanium.json`

