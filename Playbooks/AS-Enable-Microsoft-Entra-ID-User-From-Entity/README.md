# AS-Enable-Microsoft-Entra-ID-User-From-Entity
Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Enable-Microsoft-Entra-ID-User-From-Entity%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAccelerynt-Security%2FAS-Enable-Microsoft-Entra-ID-User-From-Entity%2Fmaster%2Fazuredeploy.json)    

This playbook is intended to be run from a Microsoft Sentinel entity. It will enable the Microsoft Entra ID user account associated with the Microsoft Sentinel account entity.

![Azure_AD_Enable_User_Demo_1](Images/Azure_AD_Enable_User_Demo_1.png)
![Azure_AD_Enable_User_Demo_2](Images/Azure_AD_Enable_User_Demo_2.png)

> **Note**
> This playbook is meant to be used in tandem with https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Disable-Microsoft-Entra-ID-User-From-Entity. The "**Create an App Registration**" and "**Create an Azure Key Vault Secret**" setup steps only need to be completed once, as both playbooks share the same requirements.


#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* A Microsoft Entra ID [app registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#create-an-app-registration) with admin consent granted for "**User.ManageIdentities.All**" and "**User.EnableDisableAccount.All**" in the "**Microsoft Graph**" API
* An [Azure key vault secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#create-an-azure-key-vault-secret) containing your app registration client secret

> **Note**
> This playbook uses an HTTPS request rather than the built in Microsoft Entra ID connector to update users, which is why the app registration is required. A version using the Microsoft Entra ID connector can be found here: https://github.com/Accelerynt-Security/AS-Microsoft-Entra-ID-Enable-User.


# 
### Setup

#### Create an App Registration

Navigate to the Microsoft Entra ID app registration page: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

Click "**New registration**".

![Azure_AD_Enable_User_App_Registration_1](Images/Azure_AD_Enable_User_App_Registration_1.png)

Enter "**AS-Update-Microsoft-Entra-ID-User**" for the name, all else can be left as is. Click "**Register**"

![Azure_AD_Enable_User_App_Registration_2](Images/Azure_AD_Enable_User_App_Registration_2.png)

Once the app registration is created, you will be redirected to the "**Overview**" page. Under the "**Essentials**" section, take note of the "**Application (client) ID**", as this will be needed for deployment.

![Azure_AD_Enable_User_App_Registration_3](Images/Azure_AD_Enable_User_App_Registration_3.png)

Next, you will need to add permissions for the app registration to call the [Microsoft Graph API update user endpoint](https://learn.microsoft.com/en-us/graph/api/user-update?view=graph-rest-1.0&tabs=http#permissions). From the left menu blade, click "**API permissions**" under the "**Manage**" section. Then, click "**Add a permission**".

![Azure_AD_Enable_User_App_Registration_4](Images/Azure_AD_Enable_User_App_Registration_4.png)

From the "**Select an API**" pane, click the "**Microsoft APIs**" tab and select "**Microsoft Graph**".

![Azure_AD_Enable_User_App_Registration_5](Images/Azure_AD_Enable_User_App_Registration_5.png)

Click "**Application permissions**", then scroll down to the "**User**" tab.

![Azure_AD_Enable_User_App_Registration_6](Images/Azure_AD_Enable_User_App_Registration_6.png)

Click the "**User.ManageIdentities.All**" and "**User.EnableDisableAccount.All**" options, then click "**Add permission**".

![Azure_AD_Enable_User_App_Registration_7](Images/Azure_AD_Enable_User_App_Registration_7.png)

Admin consent will be needed before your app registration can use the assigned permissions. Click "**Grant admin consent for (name)**".

![Azure_AD_Enable_User_App_Registration_8](Images/Azure_AD_Enable_User_App_Registration_8.png)

Lastly, a client secret will need to be generated for the app registration. From the left menu blade, click "**Certificates & secrets**" under the "**Manage**" section. Then, click "**New client secret**".

![Azure_AD_Enable_User_App_Registration_9](Images/Azure_AD_Enable_User_App_Registration_9.png)

Enter a description and select the desired expiration date, then click "**Add**".

![Azure_AD_Enable_User_App_Registration_10](Images/Azure_AD_Enable_User_App_Registration_10.png)

Copy the value of the secret that is generated, as this will be needed for [Create an Azure Key Vault Secret](https://github.com/Accelerynt-Security/AS-Disable-Microsoft-Entra-ID-User-From-Entity#create-an-azure-key-vault-secret).

![Azure_AD_Enable_User_App_Registration_11](Images/Azure_AD_Enable_User_App_Registration_11.png)


#### Create an Azure Key Vault Secret

Navigate to the Azure key vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing key vault or create a new one. From the key vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![Azure_AD_Enable_User_Key_Vault_1](Images/Azure_AD_Enable_User_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-Update-Microsoft-Entra-ID-User--App-Registration-Client-Secret**", and enter the client secret copied in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#create-an-app-registration). All other settings can be left as is. Click "**Create**". 

![Azure_AD_Enable_User_Key_Vault_2](Images/Azure_AD_Enable_User_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#granting-access-to-azure-key-vault).

![Azure_AD_Enable_User_Key_Vault_3](Images/Azure_AD_Enable_User_Key_Vault_3.png)


#
### Deployment

To configure and deploy this playbook:

Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-Enable-Azure-AD-User-From-Entity

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Enable-Microsoft-Entra-ID-User-From-Entity%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAccelerynt-Security%2FAS-Enable-Microsoft-Entra-ID-User-From-Entity%2Fmaster%2Fazuredeploy.json)

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.  

In the **Instance details** section:  
                                                  
* **Playbook Name**: This can be left as "**AS-Enable-Microsoft-Entra-ID-User-From-Entity**" or you may change it.

* **Client ID**: Enter the Application (client) ID of your app registration referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#create-an-app-registration).

* **Key Vault Name**: Enter the name of the key vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#create-an-azure-key-vault-secret).

* **Key Vault Secret Name**: Enter the name of the key vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Enable-Microsoft-Entra-ID-User-From-Entity#create-an-azure-key-vault-secret).


Towards the bottom, click on "**Review + create**". 

![Azure_AD_Enable_User_Deploy_1](Images/Azure_AD_Enable_User_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![Azure_AD_Enable_User_Deploy_2](Images/Azure_AD_Enable_User_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![Azure_AD_Enable_User_Deploy_3](Images/Azure_AD_Enable_User_Deploy_3.png)


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the key vault connection created during deployment must be granted access to the key vault storing your app registration client secret.

From the key vault "**Access policies**" page, click "**Create**".

![Azure_AD_Enable_User_Key_Vault_Access_1](Images/Azure_AD_Enable_User_Key_Vault_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![Azure_AD_Enable_User_Key_Vault_Access_2](Images/Azure_AD_Enable_User_Key_Vault_Access_2.png)

Paste "**AS-Enable-Microsoft-Entra-ID-User-From-Entity**" into the principal search box and click the option that appears. If the app registration also appears, select the option that does **not** match the Application (client) ID of your app registration. Click "**Next**" towards the bottom of the page.

![Azure_AD_Enable_User_Key_Vault_Access_3](Images/Azure_AD_Enable_User_Key_Vault_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![Azure_AD_Enable_User_Key_Vault_Access_4](Images/Azure_AD_Enable_User_Key_Vault_Access_4.png)
