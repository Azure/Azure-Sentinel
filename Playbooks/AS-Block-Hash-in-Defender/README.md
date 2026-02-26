# AS-Block-Hash-in-Defender

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Block-Hash-in-Defender%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Block-Hash-in-Defender%2Fazuredeploy.json)       

This playbook is intended to be run from a Microsoft Sentinel Incident. It will take the File Hashes from the Incident entities list and block them in Defender. A comment noting the affected File Hashes will be added to the Incident.
                                                                                                                                     
![BlockHashInDefender_Demo_1](Images/BlockHashInDefender_Demo_1.png)

![BlockHashInDefender_Demo_2](Images/BlockHashInDefender_Demo_2.png)


#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* A Microsoft Azure Active Directory [app registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-app-registration) with admin consent granted for "**TI.ReadWrite**" in the "**WindowsDefenderATP**" API
* An [Azure key vault secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-azure-key-vault-secret) containing your app registration client secret


# 
### Setup

#### Create an App Registration

Navigate to the Microsoft Azure Active Directory app registration page: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

Click "**New registration**".

![BlockHashInDefender_App_Registration_1](Images/BlockHashInDefender_App_Registration_1.png)

Enter "**AS-Block-Hash-in-Defender**" for the name, all else can be left as is. Click "**Register**"

![BlockHashInDefender_App_Registration_2](Images/BlockHashInDefender_App_Registration_2.png)

Once the app registration is created, you will be redirected to the "**Overview**" page. Under the "**Essentials**" section, take note of the "**Application (client) ID**", as this will be needed for deployment.

![BlockHashInDefender_App_Registration_3](Images/BlockHashInDefender_App_Registration_3.png)

Next, you will need to add permissions for the app registration to call the [Microsoft Defender submit indicator API endpoint](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/post-ti-indicator?view=o365-worldwide#permissions). From the left menu blade, click "**API permissions**" under the "**Manage**" section. Then, click "**Add a permission**".

![BlockHashInDefender_App_Registration_4](Images/BlockHashInDefender_App_Registration_4.png)

From the "**Select an API**" pane, click the "**APIs my organization uses**" tab, then paste "**WindowsDefenderATP**" in the search bar. Click the option matching the search.

![BlockHashInDefender_App_Registration_5](Images/BlockHashInDefender_App_Registration_5.png)

Click "**Application permissions**", then type "**TI.ReadAll**" into the search bar and select the result. Click "**Add permissions**".

![BlockHashInDefender_App_Registration_6](Images/BlockHashInDefender_App_Registration_6.png)

Admin consent will be needed before your app registration can use the assigned permission. Click "**Grant admin consent for (name)**".

![BlockHashInDefender_App_Registration_7](Images/BlockHashInDefender_App_Registration_7.png)

Lastly, a client secret will need to be generated for the app registration. From the left menu blade, click "**Certificates & secrets**" under the "**Manage**" section. Then, click "**New client secret**".

![BlockHashInDefender_App_Registration_8](Images/BlockHashInDefender_App_Registration_8.png)

Enter a description and select the desired expiration date, then click "**Add**".

![BlockHashInDefender_App_Registration_9](Images/BlockHashInDefender_App_Registration_9.png)

Copy the value of the secret that is generated, as this will be needed for [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-azure-key-vault-secret).

![BlockHashInDefender_App_Registration_10](Images/BlockHashInDefender_App_Registration_10.png)


#### Create an Azure Key Vault Secret

Navigate to the Azure key vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing key vault or create a new one. From the key vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![BlockHashInDefender_Key_Vault_1](Images/BlockHashInDefender_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-Block-Hash-in-Defender-AR-Client-Secret**", and enter the client secret copied in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-app-registration). All other settings can be left as is. Click "**Create**". 

![BlockHashInDefender_Key_Vault_2](Images/BlockHashInDefender_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#granting-access-to-azure-key-vault).

![BlockHashInDefender_Key_Vault_3](Images/BlockHashInDefender_Key_Vault_3.png)


#
### Deployment

To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub repository:

https://github.com/Accelerynt-Security/AS-Block-Hash-in-Defender

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Block-Hash-in-Defender%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Block-Hash-in-Defender%2Fazuredeploy.json)                                             

Click the "**Deploy to Azure**" button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the "**Subscription**" and "**Resource Group**" from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:

* **Playbook Name**: This can be left as "**AS-Block-Hash-in-Defender**" or you may change it.

* **Client ID**: Enter the Application (client) ID of your app registration referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-app-registration).

* **Key Vault Name**: Enter the name of the key vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-azure-key-vault-secret).

* **Key Vault Secret Name**: Enter the name of the key vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Block-Hash-in-Defender#create-an-azure-key-vault-secret).

Towards the bottom, click on "**Review + create**". 

![BlockHashInDefender_Deploy_1](Images/BlockHashInDefender_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![BlockHashInDefender_Deploy_2](Images/BlockHashInDefender_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![BlockHashInDefender_Deploy_3](Images/BlockHashInDefender_Deploy_3.png)


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the key vault connection created during deployment must be granted access to the key vault storing your app registration client secret.

From the key vault "**Access policies**" page, click "**Create**".

![BlockHashInDefender_Key_Vault_Access_1](Images/BlockHashInDefender_Key_Vault_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![BlockHashInDefender_Key_Vault_Access_2](Images/BlockHashInDefender_Key_Vault_Access_2.png)

Paste "**AS-Block-Hash-in-Defender**" into the principal search box and click the option that appears. Click "**Next**" towards the bottom of the page.

![BlockHashInDefender_Key_Vault_Access_3](Images/BlockHashInDefender_Key_Vault_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![BlockHashInDefender_Key_Vault_Access_4](Images/BlockHashInDefender_Key_Vault_Access_4.png)


#
### Microsoft Sentinel Contributor Role

After deployment, you will need to give the system assigned managed identity the "**Microsoft Sentinel Contributor**" role. This will enable the Logic App to add comments to Incidents. Navigate to the Log Analytics Workspaces page and select the same workspace the playbook is located in:

https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

Select the "**Access control (IAM)**" option from the menu blade, then click "**Add role assignment**".

![BlockHashInDefender_Add_Contributor_Role_1](Images/BlockHashInDefender_Add_Contributor_Role_1.png)

Select the "**Microsoft Sentinel Contributor**" role, then click "**Next**".

![BlockHashInDefender_Add_Contributor_Role_2](Images/BlockHashInDefender_Add_Contributor_Role_2.png)

Select the "**Managed identity**" option, then click "**Select Members**". Under the subscription the Logic App is located, set the value of "**Managed identity**" to "**Logic app**". Next, enter "**AS-Block-Hash-in-Defender**", or the alternative playbook name used during deployment, in the field labeled "**Select**". Select the playbook, then click "**Select**".

![BlockHashInDefender_Add_Contributor_Role_3](Images/BlockHashInDefender_Add_Contributor_Role_3.png)

Continue on to the "**Review + assign**" tab and click "**Review + assign**".

![BlockHashInDefender_Add_Contributor_Role_4](Images/BlockHashInDefender_Add_Contributor_Role_4.png)
