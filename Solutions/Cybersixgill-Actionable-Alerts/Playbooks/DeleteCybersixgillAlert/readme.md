# DeleteCybersixgillAlert
author: Loginsoft

This playbook will delete Actionable alerts in Cybersixgill Portal. When incident is deleted in Microsoft Sentinel, playbook will run and delete Actionable alerts from Portal 

# Prerequisites
We will need the following data to do one time setup

1. Cybersixgill Client ID (client_id)
2. Cybersixgill Client Secret (client_secret)

Client ID and Client Secret can be obtained from [Cybersixgill Developer Portal](https://developer.cybersixgill.com/dashboard)
* You can skip below step if you already have Client ID and Client Secret.
* Visit [Cybersixgill Developer Portal](https://developer.cybersixgill.com/dashboard)
* Click on Create an application.
* Enter Application name and brief description and optional Application image
* All other fields can be left to default.
* Once done click on Create the app.
* Copy Client ID and Client Secret.

#### Create an Azure Key Vault Secret:

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![DeleteCybersixgillAlert_Key_Vault_1](./images/DeleteCybersixgillAlert_Key_Vault_1.png)

Choose a name for the secret "**clientid**", and enter the Cybersixgill Client ID copied previously in the "**Value**" field. All other settings can be left as is. Click "**Create**".
Repeat same step and create a secret for "**clientsecret**"

![DeleteCybersixgillAlert_Key_Vault_2](./images/DeleteCybersixgillAlert_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option, also found under the "**Settings**" section on the Key Vault page menu. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Okta-NetworkZoneUpdate#granting-access-to-azure-key-vault).

![DeleteCybersixgillAlert_Key_Vault_3](./images/DeleteCybersixgillAlert_Key_Vault_3.png)

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersixgill-Actionable-Alerts%2FPlaybooks%2FDeleteCybersixgillAlert%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https%3A%2F%2Fportal.azure.us%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersixgill-Actionable-Alerts%2FPlaybooks%2FDeleteCybersixgillAlert%2Fazuredeploy.json)

# Post-deployment
1. Create new automation rule, ex: CybersixgillAlertDeleteAutomationRule
   * Trigger = Incident is Updated
   * Condition = -

*Automation rule example*
![](./images/AutomationRuleExampleDark.PNG)


![](./images/AutomationRuleExampleLight.PNG)


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the Key Vault connection created during deployment must be granted access to the Key Vault holding Cybersixgill Client ID and Client Secret.

From the Key Vault "**Access policies**" page, click "**Create**".

![DeleteCybersixgillAlert_Access_1](Images/DeleteCybersixgillAlert_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![DeleteCybersixgillAlert_Access_2](Images/DeleteCybersixgillAlert_Access_2.png)

Paste "**DeleteCybersixgillAlert**" into the principal search box and click the option that appears. Click "**Next**" towards the bottom of the page.

![DeleteCybersixgillAlert_Access_3](Images/DeleteCybersixgillAlert_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![DeleteCybersixgillAlert_Access_4](Images/DeleteCybersixgillAlert_Access_4.png)
