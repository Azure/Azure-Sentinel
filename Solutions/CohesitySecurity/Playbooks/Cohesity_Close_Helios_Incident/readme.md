# Cohesity Close Helios Incident Playbook
## Summary
This playbook closes the corresponding Helios ticket.

## Prerequisites
1. Install [this](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/readme.md) Azure function configuration.
**Note:** If you already did it for another playbook, then proceed to the deployment steps.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Close_Helios_Incident%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.

## Post-Deployment instructions
1. Grant KeyVault permissions to your playbook
* Go to _[Key vaults](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults)_ and choose your keyvault, which starts from _cohesitypro_ and is followed by a sequence of letters and numbers, e.g. _cohesityprofnxj32cucakwk_.
* On the right pane, click _+Create_.
* Choose _Get_ permission in the _Secret Permissions_ section and press _Next_.
* Enter your playbook name and press _Next_.
* Presss _Next_ and then _Create_ to finish granting permissions.

## Troubleshooting
1. If you'd like to use this playbook without installing the [Azure functions configuration](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/readme.md), then you need to do a few manual steps _before_ deployment.
* Create the _DataHawk API_ key:
  * Go to the Cohesity Helios [login](https://helios.cohesity.com/#/login) page.
  * Enter your credentials and select _Log In_. The _Summary_ page is displayed.
  * Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
  * Select _Add API Key_. The API Key Details is displayed.
  * Enter a name for the API key.
  * Select _Save_.
* Create your Azure KeyVault (see [instructions](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal)).
  * Create the _ApiKey_ secret and assign the _API Key_ value from the previous step to it. Now your API key is securely saved in the Azure KeyVault.
2. If you see the _Forbidden_ error message in the Keyvault block when you run the playbook, you can always authorize it manualy
* Choose your app in the [Logic Apps](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Logic%2Fworkflows)
* Authorize your KeyVault connection by selecting it and clicking on _General\Edit API Connection_
* Press the _Authorize_ button and select the appropriate account. Enter your key vault name if prompted. You can find your key vault name [here](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults).
* **Note**: If you can't authorize the connections using the steps above, you can always open your playbook in _Development Tools\Logic App Designer_, click on the connection block, and then click on the _Change connection_ link in the right pane. Then you can either create a new connection, choose a different one or authorize the one that is marked with an "i" sign.

#  References
- [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
