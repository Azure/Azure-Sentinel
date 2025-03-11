# Restore From Last Cohesity Snapshot Playbook
## Summary
This playbook restores the latest good Data Hawk (Helios) snapshot. It’s recommended for running by Backup Admins _only_ after they make sure that the existing data is compromised, and rollback to the previous snapshot, even at the expense of data loss, is _really required_. __Please beware__: It's operable only if you have installed the [Function Apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/readme.md) and received some incidents that need an action on affected data.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Restore_From_Last_Snapshot%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.

## Post-Deployment instructions
1. Make sure the user that runs the playbook has the role _Microsoft Sentinel Playbook Operator_ assigned. To assign the role,
* Under the _Subscriptions_ tab from the _Home_ page, choose your subscription name.
* Choose the _Access Control (IAM)_ option from the left pane.
* Click on _Add > Add Role Assignment_ and add _Microsoft Sentinel Playbook Operator_ to the user.

2. Authorize all connections
* Go to _Logic Apps_ and choose your playbook
* In the _Development Tools_ sections select _API Connections_. In the left pane you'll see the list of connections that you'll need to authorize
  * Authorize the Azure blob storage connection by selecting it and clicking on _General\Edit API Connection_
    * Enter your connection name, storage account and access key. You can find them by selecting your storage account [here](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) and then choosing _Security+networking\Access keys_).

2. Grant KeyVault permissions to your playbook
* Go to _[Key vaults](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults)_ and choose your keyvault, which starts from _cohesitypro_ and is followed by a sequence of letters and numbers, e.g. _cohesityprofnxj32cucakwk_.
* On the right pane, select _Access Policies_ and click _+Create_.
* Choose _Get_ permission in the _Secret Permissions_ section and press _Next_.
* Enter your playbook name and press _Next_.
* Press _Next_ and then _Create_ to finish granting permissions.

3. (_Recommendation_) Limit access rights to this playbook to only Backup Admins because this playbook rolls back customer data that can result in a loss of important data if used without a good reason.
* From the Microsoft Sentinel navigation menu, select _Settings_.
* In the _Settings_ blade, select the _Settings_ tab and expand _Playbook Permissions_.
* Select _Configure Permissions_ to open the _Manage Permissions_ panel.
* Select the required resource group and click _Apply_.
* Select _Done_.

## Troubleshooting
1. If your API key expired, then you need to replace it with a new one.
* Create the Cohesity _Helios API_ key:
  * Go to the Cohesity Helios [login](https://helios.cohesity.com/#/login) page.
  * Enter your credentials and select _Log In_. The _Summary_ page is displayed.
  * Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
  * Select _Add API Key_. The API Key Details is displayed.
  * Enter a name for the API key.
  * Select _Save_.
* Go to _[Key vaults](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults)_ and choose your keyvault, which starts from _cohesitypro_ and is followed by a sequence of letters and numbers, e.g. _cohesityprofnxj32cucakwk_.
  * Assign the _ApiKey_ secret to the _API Key_ value from the previous step. Now your API key is securely saved in the Azure KeyVault.
2. If you see the _Forbidden_ error message in the Keyvault block when you run the playbook, you can always authorize it manually.
* Choose your app in the [Logic Apps](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Logic%2Fworkflows)
* Authorize your KeyVault connection by selecting it and clicking on _General\Edit API Connection_
* Press the _Authorize_ button and select the appropriate account. Enter your key vault name if prompted. You can find your key vault name [here](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults).
* **Note**: If you can't authorize the connections using the steps above, you can always open your playbook in _Development Tools\Logic App Designer_, click on the connection block, and then click on the _Change connection_ link in the right pane. Then you can either create a new connection, choose a different one or authorize the one that is marked with an "i" sign.

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm).
