# Deploy widgets

To deploy widgets to a workspace:

## Create a Key Vault to store widgets credentials

1. Onboard to Azure Cloud Shell - Perform the following 2 steps from the doc [Azure Cloud Shell Quick Start Guide](https://learn.microsoft.com/en-us/azure/cloud-shell/quickstart?tabs=azurecli):

- Start Cloud Shell
- Select your shell environment - **PowerShell**

2. Run the following commands within the **Azure Cloud Shell**:
* Copy the KeyVault provisioning script:
``` Command Line
Invoke-WebRequest -Uri https://aka.ms/SentinelWidgetsDeployScript -OutFile WidgetsKvCreation.Ps1
```

* Run the KeyVault provisioning script (You can get the SubscriptionId and WorkspaceId by choosing `Settings`->`Workspace Settings` in your Sentinel workspace):
``` Command Line
./WidgetsKvCreation.Ps1 -SubscriptionId <subscription id> -WorkspaceId <workspace id>
```

* Make sure you record the KeyVault name that the script prints, as you will need it to configure the widgets. If you did not record the name, you can either re-run the script, or search for the Keyvault name ("widgets-...") in Azure Portal: [Key Vaults](https://ms.portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults).
* Notice: You can Verify that the "widgets-..." KeyValut is matched to the workspace, by entering the 'Tags' page of the KeyVault within AzurePortal, and check that the **WorkspaceId** tag matches the workspace Id of your Setninel workspace.

## Configure widgets

For each widget, configure the secrets and other parameters it reqruies using the links below, which will help you to store them in the workspace Key Vault.

- [Configure Anomali](https://aka.ms/SentinelWidgetsAnomaliARM)
- [Configure Recorded Future](https://aka.ms/SentinelWidgetsRecordedFutureARM)
