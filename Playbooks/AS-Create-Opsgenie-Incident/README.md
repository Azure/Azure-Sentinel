# AS-Create-Opsgenie-Incident

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Create-Opsgenie-Incident%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Create-Opsgenie-Incident%2Fazuredeploy.json)

![Opsgenie_Demo_2](Images/Opsgenie_Demo_2.png)

This playbook is intended to be run from a Microsoft Sentinel Incident. It will create either an incident or an alert in Opsgenie with the information from a Microsoft Sentinel incident.

![Opsgenie_Demo_1](Images/Opsgenie_Demo_1.png)

This playbook maps Microsoft Sentinel incident severity over to Opsgenie incident/alert priority like so:

| **Microsoft Sentinel**  |   **Opsgenie**       |
| ----------------------  |   ------------       |
|  High	                  |    P2 - High         |
|  Medium                 |    P3 - Moderate     |
|  Low	                  |    P4 - Low          |
|  Informational          |    P5 - Informational|

#
### Requirements

The following items are required under the template settings during deployment: 

* An Opsgenie account and an [API integration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Create-Opsgenie-Incident#create-an-opsgenie-api-integration)
* For creating Opsgenie [incidents](https://docs.opsgenie.com/docs/incident-api), a standard or enterprise plan is needed. This is not a requirement for creating Opsgenie [alerts](https://docs.opsgenie.com/docs/alert-api). It should be noted that structurally, incident and alert objects are nearly identical in Opsgenie, and either works well with Microsoft Sentinel incident data. If you are using a trial account, select the alert endpoint during deployment
* An [Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Create-Opsgenie-Incident#create-an-azure-key-vault-secret) containing your Okta API Token 

# 
### Setup

#### Create an Opsgenie API integration

From your Opsgenie account, select the "**Teams**" tab, and then click "**Add Team**".

![opsgenie_setup_1](Images/opsgenie_setup_1.png)

Enter "**Microsoft Sentinel**" in the name field and add an optional description, then click "**Add team**".

![opsgenie_setup_2](Images/opsgenie_setup_2.png)

From the newly created team page, navigate to "**Integrations**" from the left menu blade, then click "**Add integration**".

![opsgenie_setup_3](Images/opsgenie_setup_3.png)

Although there are pre-built integration apps for Microsoft Azure, there is currently not one for Microsoft Sentinel, therefore the "**API**" integration must be selected.

![opsgenie_setup_4](Images/opsgenie_setup_4.png)

Take note of the "**API Key**" that is generated, as it will be needed later, then click "**Save integration**".

![opsgenie_setup_5](Images/opsgenie_setup_5.png)

#### Create an Azure Key Vault Secret:

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![Opsgenie_Key_Vault_1](Images/Opsgenie_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-Create-Opsgenie-Incident-API-Key**", and enter the Opsgenie API Key copied previously in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Create-Opsgenie-Incident#create-an-opsgenie-api-integration). All other settings can be left as is. Click "**Create**". 

![Opsgenie_Key_Vault_2](Images/Opsgenie_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option, also found under the "**Settings**" section on the Key Vault page menu. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Create-Opsgenie-Incident#granting-access-to-azure-key-vault).

![Opsgenie_Key_Vault_3](Images/Opsgenie_Key_Vault_3.png)

#
### Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-Create-Opsgenie-Incident

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Create-Opsgenie-Incident%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Create-Opsgenie-Incident%2Fazuredeploy.json)                                             

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as "**AS-Create-Opsgenie-Incident**" or you may change it.

* **Opsgenie Endpoint**: This can be left as "**/v1/incidents/create**" if mapping Microsoft Sentinel incidents to Opsgenie incidents, or changed to "**/v2/alerts**"  if mapping Microsoft Sentinel incidents to Opsgenie alerts.

* **Key Vault Name**: Enter the name of the Key Vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Create-Opsgenie-Incident#create-an-azure-key-vault-secret).

* **Secret Name**: Enter the name of the Key Vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Create-Opsgenie-Incident#create-an-azure-key-vault-secret).

Towards the bottom, click on “**Review + create**”. 

![Opsgenie_Deploy_1](Images/Opsgenie_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![Opsgenie_Deploy_2](Images/Opsgenie_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
To view the deployed Logic App, click the resource that corresponds to it.

![Opsgenie_Deploy_3](Images/Opsgenie_Deploy_3.png)

#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the Key Vault connection created during deployment must be granted access to the Key Vault storing your Okta API Token.

From the Key Vault "**Access policies**" page, click "**Create**".

![Opsgenie_Access_1](Images/Opsgenie_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![Opsgenie_Access_2](Images/Opsgenie_Access_2.png)

Paste "**AS-Create-Opsgenie-Incident**" into the principal search box and click the option that appears. Click "**Next**" towards the bottom of the page.

![Opsgenie_Access_3](Images/Opsgenie_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![Opsgenie_Access_4](Images/Opsgenie_Access_4.png)
