# Deploy widgets

To deploy widgets to a workspace:

## Create a Key Vault to store widgets credentials

Download the [Deployment/WidgetsKvCreation](https://aka.ms/SentinelWidgetsDeployScript) powershell script. and then execute it using the following steps: #TODO: need to update the aka.ms

1. Onboard to Azure cloud Shell: [Azure Cloud Shell](https://learn.microsoft.com/en-us/azure/cloud-shell/quickstart?tabs=azurecli)
Perform the following setps from the doc:
- Start Cloud Shell
- Select your shell environment - **PowerShell**

2. Run the following command within the Azure Cloud shell
``` Command Line
./WidgetsKvCreation.Ps1 -SubscriptionId <subscription id> -WorkspaceId <workspace id>

```

* You can get the SubscriptionId and WorkspaceId by choosing `Settings`->`Workspace Settings` in your Sentinel workspace.

* Make sure you record the Key Vault name that the script prints, as you will need it to configure the widgets. If you did not record the name, you can either re-run the script, or search for the Keyvault (which has a "widgets" prefix) in [Key Vaults](https://ms.portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults).
* Notice: You can Verify that the "widgets-*" KeyValut is matched to the workspace, by entering the KeyVault => Tags page, and check that the WorkspaceId tag matches the workspace Id of your Setninel workspace.

## Configure widgets

For each widget, configure the secrets and other parameters it reqruies using the links below, which will help you to store them in the workspace Key Vault.

- [Configure Anomali](https://aka.ms/SentinelWidgetsAnomaliARM)
- [Configure Recorded Future](https://aka.ms/SentinelWidgetsRecordedFutureARM)
