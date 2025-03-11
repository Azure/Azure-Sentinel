# AS-MDE-Isolate-Machine

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-MDE-Isolate-Machine%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-MDE-Isolate-Machine%2Fazuredeploy.json)       

This playbook is intended to be run from a Microsoft Sentinel incident. It will match the hosts from a Microsoft Sentinel incident with Microsoft Defender machines and isolate them in Defender. A comment noting the affected machines will be added to the Microsoft Sentinel incident.
                                                                                                                                     
![IsolateMachine_Demo_1](Images/IsolateMachine_Demo_1.png)


#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* A Microsoft Azure Active Directory [app registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-app-registration) with admin consent granted for "**Machine.Isolate**" in the "**WindowsDefenderATP**" API
* An [Azure key vault secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-azure-key-vault-secret) containing your app registration client secret


> **Note**
> This playbook is meant to be used in tandem with https://github.com/Accelerynt-Security/AS-MDE-Unisolate-Machine. The "**Create an App Registration**" and "**Create an Azure Key Vault Secret**" setup steps only need to be completed once, as both playbooks share the same requirements.


# 
### Setup

#### Create an App Registration

Navigate to the Microsoft Azure Active Directory app registration page: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

Click "**New registration**".

![IsolateMachine_App_Registration_1](Images/IsolateMachine_App_Registration_1.png)

Enter "**AS-MDE-Isolate-Machine**" for the name, all else can be left as is. Click "**Register**".

![IsolateMachine_App_Registration_2](Images/IsolateMachine_App_Registration_2.png)

Once the app registration is created, you will be redirected to the "**Overview**" page. Under the "**Essentials**" section, take note of the "**Application (client) ID**", as this will be needed for deployment.

![IsolateMachine_App_Registration_3](Images/IsolateMachine_App_Registration_3.png)

Next, you will need to add permissions for the app registration to call the [Microsoft Defender Isolate machine endpoint](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/api/isolate-machine?view=o365-worldwide#http-request). From the left menu blade, click "**API permissions**" under the "**Manage**" section. Then, click "**Add a permission**".

![IsolateMachine_App_Registration_4](Images/IsolateMachine_App_Registration_4.png)

From the "**Select an API**" pane, click the "**APIs my organization uses**" tab, then paste "**WindowsDefenderATP**" in the search bar. Click the option matching the search.

![IsolateMachine_App_Registration_5](Images/IsolateMachine_App_Registration_5.png)

Click "**Application permissions**", then type "**Machine.Isolate**" into the search bar and select the result. Click "**Add permissions**".

![IsolateMachine_App_Registration_6](Images/IsolateMachine_App_Registration_6.png)

Admin consent will be needed before your app registration can use the assigned permission. Click "**Grant admin consent for (name)**".

![IsolateMachine_App_Registration_7](Images/IsolateMachine_App_Registration_7.png)

Lastly, a client secret will need to be generated for the app registration. From the left menu blade, click "**Certificates & secrets**" under the "**Manage**" section. Then, click "**New client secret**". Enter a description and select the desired expiration date, then click "**Add**".

![IsolateMachine_App_Registration_8](Images/IsolateMachine_App_Registration_8.png)

Copy the value of the secret that is generated, as this will be needed for [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-azure-key-vault-secret).

![IsolateMachine_App_Registration_9](Images/IsolateMachine_App_Registration_9.png)


#### Create an Azure Key Vault Secret

Navigate to the Azure key vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing key vault or create a new one. From the key vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![IsolateMachine_Key_Vault_1](Images/IsolateMachine_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-MDE-Isolate-Machine--AR-Client-Secret**", and enter the client secret copied in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-app-registration). All other settings can be left as is. Click "**Create**". 

![IsolateMachine_Key_Vault_2](Images/IsolateMachine_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#granting-access-to-azure-key-vault).

![IsolateMachine_Key_Vault_3](Images/IsolateMachine_Key_Vault_3.png)


#
### Deployment

To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub repository:

https://github.com/Accelerynt-Security/AS-MDE-Isolate-Machine

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-MDE-Isolate-Machine%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-MDE-Isolate-Machine%2Fazuredeploy.json)                                             

Click the "**Deploy to Azure**" button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the "**Subscription**" and "**Resource Group**" from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:

* **Playbook Name**: This can be left as "**AS-MDE-Isolate-Machine**" or you may change it.

* **Client ID**: Enter the Application (client) ID of your app registration referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-app-registration).

* **Key Vault Name**: Enter the name of the key vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-azure-key-vault-secret).

* **Secret Name**: Enter the name of the key vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-MDE-Isolate-Machine#create-an-azure-key-vault-secret).

Towards the bottom, click on "**Review + create**". 

![IsolateMachine_Deploy_1](Images/IsolateMachine_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![IsolateMachine_Deploy_2](Images/IsolateMachine_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![IsolateMachine_Deploy_3](Images/IsolateMachine_Deploy_3.png)


#
### Microsoft Sentinel Contributor Role

After deployment, you will need to give the system assigned managed identity the "**Microsoft Sentinel Contributor**" role. This will enable it to add comments to incidents. Navigate to the Log Analytics Workspaces page and select the same workspace the playbook is located in:

https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

Select the "**Access control (IAM)**" option from the menu blade, then click "**Add role assignment**".

![IsolateMachine_Add_Contributor_Role_1](Images/IsolateMachine_Add_Contributor_Role_1.png)

Select the "**Microsoft Sentinel Contributor**" role, then click "**Next**".

![IsolateMachine_Add_Contributor_Role_2](Images/IsolateMachine_Add_Contributor_Role_2.png)

Select the "**Managed identity**" option, then click "**Select Members**". Under the subscription the logic app is located, set the value of "**Managed identity**" to "**Logic app**". Next, enter "**AS-MDE-Isolate-Machine**", or the alternative playbook name used during deployment, in the field labeled "**Select**". Select the playbook, then click "**Select**".

![IsolateMachine_Add_Contributor_Role_3](Images/IsolateMachine_Add_Contributor_Role_3.png)

Continue on to the "**Review + assign**" tab and click "**Review + assign**".

![IsolateMachine_Add_Contributor_Role_4](Images/IsolateMachine_Add_Contributor_Role_4.png)


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the key vault connection created during deployment must be granted access to the key vault storing your app registration client secret.

From the key vault "**Access policies**" page, click "**Create**".

![IsolateMachine_Key_Vault_Access_1](Images/IsolateMachine_Key_Vault_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![IsolateMachine_Key_Vault_Access_2](Images/IsolateMachine_Key_Vault_Access_2.png)

Paste "**AS-MDE-Isolate-Machine**" into the principal search box and click the option that appears. Click "**Next**" towards the bottom of the page.

![IsolateMachine_Key_Vault_Access_3](Images/IsolateMachine_Key_Vault_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![IsolateMachine_Key_Vault_Access_4](Images/IsolateMachine_Key_Vault_Access_4.png)
