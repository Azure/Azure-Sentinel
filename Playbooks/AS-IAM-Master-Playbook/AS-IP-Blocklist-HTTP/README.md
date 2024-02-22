# AS-IP-Blocklist-HTTP

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Master-Playbook%2FAS-IP-Blocklist-HTTP%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Master-Playbook%2FAS-IP-Blocklist-HTTP%2Fazuredeploy.json)       

This playbook is intended to be run from the AS-IAM-Master-Playbook. It will add the IP address from Microsoft Sentinel Incidents to a Microsoft Azure Conditional Access Named Locations list, indicating compromised IP addresses.
                                                                                                                                     
![NamedLocations_Demo](Images/NamedLocations_Demo.png)
 
                                                                                                                                     
#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* A Microsoft Azure [Named Locations List](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-a-named-locations-list)
* An [App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-app-registration) for using the Microsoft Graph API
* An [Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-azure-key-vault-secret) containing your App Registration Secret 


# 
### Setup
                                                                                                                                     
#### Create a Named Locations list:

Navigate to the Microsoft Azure Active Directory Menu:

https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Overview

From there, click the "**Security**" menu option.

![NamedLocations_Create_List_1](Images/NamedLocations_Create_List_1.png)

Navigate to the "**Named locations**" menu option and then click "**IP ranges location**".

![NamedLocations_Create_List_2](Images/NamedLocations_Create_List_2.png)

Create a name for your Named Locations list. The list cannot be saved without an initiating value. It should be noted IPs are only accepted in a CIDR range notation. Individual IPs processed by this playbook will have a "**/32**" appended to them to fit this format.

![NamedLocations_Create_List_3](Images/NamedLocations_Create_List_3.png)

The name of your Named Locations list, along with its ID, should be noted, as these will be required for the deployment of this playbook. 

The list ID may be more difficult to track down, as it is currently not displayed in the URL upon selection. Our solution for this was to send a GET request from https://developer.microsoft.com/en-us/graph/graph-explorer to the following endpoint: https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations.

The JSON response body includes all Named Location lists, along with their IDs.


#### Create an App Registration:
 
Navigate to the Navigate to the Microsoft Azure Active Directory App Registrations page:

https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

From there, click "**New registration**".

![NamedLocations_Create_App_Registration_1](Images/NamedLocations_Create_App_Registration_1.png)

Select a name for your App Registration, such as "**AS-IP-Blocklist-HTTP**", then click "**Register**".

![NamedLocations_Create_App_Registration_2](Images/NamedLocations_Create_App_Registration_2.png)

From the application menu blade, select "**API permissions**" and then click "**Add a permission**". Click the "**Microsoft Graph**" category.

![NamedLocations_Create_App_Registration_3](Images/NamedLocations_Create_App_Registration_3.png)

Under "**Application permissions**", search for "**Policy**", then select the "**Policy.Read.All**" and ""**Policy.ReadWrite.ConditionalAccess**" checkboxes. Click "**Add permissions**".

![NamedLocations_Create_App_Registration_4](Images/NamedLocations_Create_App_Registration_4.png)

In order for these permissions to be applied, admin consent must also be granted. Click the indicated "**Grant admin consent**" button on the "**API permissions**" page.
![NamedLocations_Create_App_Registration_5_consent](Images/NamedLocations_Create_App_Registration_5_consent.png)

Navigate back to the "**Overview**" section on the menu and take note of the "**Application (client) ID**" and "**Directory (tenant) ID**, as each will be needed for the deployment of this playbook. Click "**Add a certificate or secret**".

![NamedLocations_Create_App_Registration_5](Images/NamedLocations_Create_App_Registration_5.png)

Click "**New client secret"**". After adding a description and selecting an expiration date, click "**Add**".

![NamedLocations_Create_App_Registration_6](Images/NamedLocations_Create_App_Registration_6.png)

Copy the generated "**Value**" and save it for the next step, [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-azure-key-vault-secret).

![NamedLocations_Create_App_Registration_7](Images/NamedLocations_Create_App_Registration_7.png)


#### Create an Azure Key Vault Secret:

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![NamedLocations_Key_Vault_1](Images/NamedLocations_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-IP-Blocklist-HTTP-App-Registration-Secret**", and enter the App Registration Secret copied previously in the "**Value**" field. All other settings can be left as is. Click "**Create**". 

![NamedLocations_Key_Vault_2](Images/NamedLocations_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option, also found under the "**Settings**" section on the Key Vault page menu. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#granting-access-to-azure-key-vault).

![NamedLocations_Key_Vault_3](Images/NamedLocations_Key_Vault_3.png)


#
### Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-IAM-Master-Playbook/tree/main/AS-IP-Blocklist-HTTP

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Master-Playbook%2FAS-IP-Blocklist-HTTP%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Master-Playbook%2FAS-IP-Blocklist-HTTP%2Fazuredeploy.json)                                             

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as "**AS-IP-Blocklist-HTTP**" or you may change it.  

* **Named Locations List Name**: Enter the value of the Named Locations list created in [Create a Named Locations list](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-a-named-locations-list).

* **Named Locations List ID**: Enter the value of the Named Locations list ID referenced in [Create a Named Locations list](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-a-named-locations-list).

* **App Registration ID**: Enter the value of the Application (client) ID referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-app-registration).

* **App Registration Tenant**: Enter the value of the Directory (tenant) ID referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-app-registration).

* **Key Vault Name**: Enter the name of the Key Vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-azure-key-vault-secret).

* **Secret Name**: Enter the name of the Key Vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-IAM-Master-Playbook/AS-IP-Blocklist-HTTP#create-an-azure-key-vault-secret).

Towards the bottom, click on “**Review + create**”. 

![NamedLocations_Deploy_1](Images/NamedLocations_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![NamedLocations_Deploy_2](Images/NamedLocations_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "Deployment details" section to view them. To view the deployed Logic App, click the resource that corresponds to it.

![NamedLocations_Deploy_3](Images/NamedLocations_Deploy_3.png)


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the Key Vault connection created during deployment must be granted access to the Key Vault storing your App Registration Secret.

From the Key Vault "**Access policies**" page, click "**Add Access Policy**".

![NamedLocations_Access_1](Images/NamedLocations_Access_1.png)

Select the "**Get**" checkbox in the "**Secret permissions**" list field. Then click the blue "**None selected**" text next to the "**Select principal**" field.

Paste "**AS-IP-Blocklist-HTTP**" into the principal search box and click the option that appears. Click "**Select**" towards the bottom of the page.

![NamedLocations_Access_2](Images/NamedLocations_Access_2.png)

Click "**Add**".

![NamedLocations_Access_3](Images/NamedLocations_Access_3.png)


#
### Microsoft Sentinel Contributor Role

After deployment, you will need to give the system assigned managed identity the "**Microsoft Sentinel Contributor**" role. This will enable the Logic App to add comments to Incidents. Navigate to the Log Analytics Workspaces page and select the same workspace the playbook is located in:

https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

Select the "**Access control (IAM)**" option from the menu blade, then click "**Add role assignment**".

![NamedLocations_Add_Contributor_Role_1](Images/NamedLocations_Add_Contributor_Role_1.png)

Select the "**Microsoft Sentinel Contributor**" role, then click "**Next**".

![NamedLocations_Add_Contributor_Role_2](Images/NamedLocations_Add_Contributor_Role_2.png)

Select the "**Managed identity**" option, then click "**Select Members**". Under the subscription the Logic App is located, set the value of "**Managed identity**" to "**Logic app**". Next, enter "**AS-Microsoft-Entra-ID-Revoke-User-Sessions-HTTP**", or the alternative playbook name used during deployment, in the field labeled "**Select**". Select the playbook, then click "**Select**".

![NamedLocations_Add_Contributor_Role_3](Images/NamedLocations_Add_Contributor_Role_3.png)

Continue on to the "**Review + assign**" tab and click "**Review + assign**".

![NamedLocations_Add_Contributor_Role_4](Images/NamedLocations_Add_Contributor_Role_4.png)
