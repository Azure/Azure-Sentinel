# AS-Incident-Response-Approval-Email

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Incident-Response-Approval-Email%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Incident-Response-Approval-Email%2Fazuredeploy.json)       

This playbook is intended to be run from a Microsoft Sentinel incident. It will facilitate incident response by sending an approval email to the manager(s) of the user(s) associated with the Microsoft Sentinel incident.

![ApprovalEmail_Demo](Images/ApprovalEmail_Demo.png)
 
                                                                                                                                
#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* An [App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-app-registration) for using the Microsoft Graph API
* An [Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-azure-key-vault-secret) containing your App Registration Secret 


# 
### Setup
                                                                                                                                     
#### 1. Create an App Registration:
 
Navigate to the Navigate to the Microsoft Azure Active Directory App Registrations page:

https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

From there, click "**New registration**".

![ApprovalEmail_Create_App_Registration_1](Images/ApprovalEmail_Create_App_Registration_1.png)

Select a name for your App Registration, such as "**AS-Incident-Response-Approval-Email-AR**", then click "**Register**".

![ApprovalEmail_Create_App_Registration_2](Images/ApprovalEmail_Create_App_Registration_2.png)

From the application menu blade, select "**API permissions**" and then click "**Add a permission**". Click the "**Microsoft Graph**" category.

![ApprovalEmail_Create_App_Registration_3](Images/ApprovalEmail_Create_App_Registration_3.png)

Under "**Application permissions**", search for "**User.Read.All**", then select the corresponding checkbox. Click "**Add permissions**".

![ApprovalEmail_Create_App_Registration_4](Images/ApprovalEmail_Create_App_Registration_4.png)

In order for these permissions to be applied, admin consent must also be granted. Click the indicated "**Grant admin consent**" button on the "**API permissions**" page.
![ApprovalEmail_Create_App_Registration_5_consent](Images/ApprovalEmail_Create_App_Registration_5.png)

Navigate back to the "**Overview**" section on the menu and take note of the "**Application (client) ID**" and "**Directory (tenant) ID**, as each will be needed for the deployment of this playbook. Click "**Add a certificate or secret**".

![ApprovalEmail_Create_App_Registration_6](Images/ApprovalEmail_Create_App_Registration_6.png)

Click "**New client secret"**". After adding a description and selecting an expiration date, click "**Add**".

![ApprovalEmail_Create_App_Registration_7](Images/ApprovalEmail_Create_App_Registration_7.png)

Copy the generated "**Value**" and save it for the next step, [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-azure-key-vault-secret).

![ApprovalEmail_Create_App_Registration_8](Images/ApprovalEmail_Create_App_Registration_8.png)


#### 2. Create an Azure Key Vault Secret:

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![ApprovalEmail_Key_Vault_1](Images/ApprovalEmail_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-Incident-Response-Approval-Email-App-Registration-Secret**", and enter the App Registration Secret copied previously in the "**Value**" field. All other settings can be left as is. Click "**Create**". 

![ApprovalEmail_Key_Vault_2](Images/ApprovalEmail_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option on the Key Vault page menu. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#granting-access-to-azure-key-vault).

![ApprovalEmail_Key_Vault_3](Images/ApprovalEmail_Key_Vault_3.png)


#
### 3. Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-Incident-Response-Approval-Email

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Incident-Response-Approval-Email%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Incident-Response-Approval-Email%2Fazuredeploy.json)                                             

Click the "**Deploy to Azure**" button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the "**Subscription**" and "**Resource Group**" from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as "**AS-Incident-Response-Approval-Email**" or you may change it.  

* **App Registration ID**: Enter the value of the Application (client) ID referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-app-registration).

* **App Registration Tenant**: Enter the value of the Directory (tenant) ID referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-app-registration).

* **Key Vault Name**: Enter the name of the Key Vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-azure-key-vault-secret).

* **Secret Name**: Enter the name of the Key Vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Incident-Response-Approval-Email#create-an-azure-key-vault-secret).

Towards the bottom, click on "**Review + create**". 

![ApprovalEmail_Deploy_1](Images/ApprovalEmail_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![ApprovalEmail_Deploy_2](Images/ApprovalEmail_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![ApprovalEmail_Deploy_3](Images/ApprovalEmail_Deploy_3.png)

Click on the "**Edit**" button. This will bring us into the Logic Apps Designer.

![ApprovalEmail_Deploy_4](Images/ApprovalEmail_Deploy_4.png)

The step labeled "**Connections**" uses an Office365 connection created during the deployment of this playbook. Before the playbook can be run, this connection will either need to be authorized in the indicated step, or an existing authorized connection may be alternatively selected.

![ApprovalEmail_Deploy_5](Images/ApprovalEmail_Deploy_5.png)

To validate the connection, expand the "**Connections**" step and click the exclamation point icon next to the name matching the playbook.
                                                                                                
![ApprovalEmail_Deploy_6](Images/ApprovalEmail_Deploy_6.png)

When prompted, sign in to validate the connection.                                                                                                
                                                                                                
![ApprovalEmail_Deploy_7](Images/ApprovalEmail_Deploy_7.png)


#
### 4. Granting Access to Azure Key Vault

Before the Logic App can run successfully, the Key Vault connection created during deployment must be granted access to the Key Vault storing your App Registration Secret.

From the Key Vault "**Access policies**" page, click "**Create**".

![ApprovalEmail_Access_1](Images/ApprovalEmail_Access_1.png)

Select the "**Get**" checkbox in the "**Secret permissions**" section. Then click "**Next**".

![ApprovalEmail_Access_2](Images/ApprovalEmail_Access_2.png)

From the "**Principal**" page, paste "**AS-Incident-Response-Approval-Email**", or the alternative playbook name you used, into the search box and click the option that appears. Click "**Next**". 

* Note that if the same name is used for the app registration and playbook, you will see two options here, which can be hard to differentiate. In this case, you would want to select the option whose ID does **not** match the app registration (client) ID.

![ApprovalEmail_Access_3](Images/ApprovalEmail_Access_3.png)

Click "**Next**" in the application section. Then from the "**Review + create**" page, click "**Create**".

![ApprovalEmail_Access_4](Images/ApprovalEmail_Access_4.png)
