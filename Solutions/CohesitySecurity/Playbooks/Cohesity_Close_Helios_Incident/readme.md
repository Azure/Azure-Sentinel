# Cohesity Close Helios Incident Playbook
## Summary
This playbook closes the corresponding Helios ticket.

## Prerequisites
1. Create the _DataHawk API_ key:
* Go to the Cohesity DataHawk [login](https://helios.cohesity.com/#/login) page.
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_.
2. Create your Azure key vault (see [instructions](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal)).
* Create the _ApiKey_ secret and assign the _API Key_ value from the previous step to it. Now your API key is securely saved in the Azure KeyVault.
**Note:** If you already did these steps for [another playbook](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Playbooks/Cohesity_Restore_From_Last_Snapshot#readme), then you can skip them and reuse the same _ApiKey_ secret for this one.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Close_Helios_Incident%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.

## Post-Deployment instructions
1. Authorize all connections
* Go to _Logic Apps_ and choose your playbook
* In the _Developmnet Tools_ sections select _API Connections_. In the left pane you'll see the list of connections that you'll need to authorize
  * Authorize the storage connection by selecting it and clicking on _General\Edit API Connection_
    * Enter your connection name, storage account and access key. You can find them by selecting your storage account [here](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) and then choosing _Security+networking\Access keys_).
  * Authorize your KeyVault connection by selecting it and clicking on _General\Edit API Connection_
    * Press the _Authorize_ button and select the appropriate account. Enter your key vault name if prompted. You can find your key vault name [here](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults).
* **Note**: If you can't authorize the connections using the steps above, you can always open your playbook in _Development Tools\Logic App Designer_, click on every connection block, and then click on the _Change connection_ link in the right pane. Then you can either create a new connection, choose a different one or authorize the one that is marked with an "i" sign.

#  References
- [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
