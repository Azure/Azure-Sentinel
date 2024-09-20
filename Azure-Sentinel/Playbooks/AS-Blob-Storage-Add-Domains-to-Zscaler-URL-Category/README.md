# AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category%2Fazuredeploy.json)    

This playbook will use an Azure blob storage file to maintain a Zscaler custom URL category of your choice. The logic app is set to run every 5 minutes polling this blob storage file for changes. If any changes are made to the blob storage file, the Zscaler URL category values will be updated to match the file exactly. This will enable you to manage your Zscaler custom URL categories entirely from Microsoft Sentinel.
Blob storage was opted for because unlike Microsoft Sentinel watchlists, the lastModified time attribute reflects changes to the contents of the file.

![Zscaler_Demo_1](Images/Zscaler_Demo_1.png)

![Zscaler_Demo_2](Images/Zscaler_Demo_2.png)

#
### Requirements

The following items are required under the template settings during deployment: 

* The [root domain](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#zscaler-root-domain) of your Zscaler organization
* A configured Zscaler [admin account](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#zscaler-admin-account)
* A Zscaler [API key](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#zscaler-api-key)
* The name of the [Zscaler custom URL category](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#zscaler-url-category) you wish to add the Microsoft Sentinel incident domains to
* A Microsoft Azure [key vault secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#create-an-azure-key-vault-secret) containing your Okta API Token
* A Microsoft Azure [integration account](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#create-an-integration-account)
* A Microsoft Azure [blob storage file](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#create-azure-blob-storage-file)

# 
### Setup


#### Zscaler Root Domain

Navigate to https://www.zscaler.com/ and expand the dropdown list under "**Sign In**". The value you enter for the "**Zscaler Root Domain**" deployment parameter should exactly match the format of the options shown here. Select your appropriate domain and log in.

![Zscaler_Root_Domain_1](Images/Zscaler_Root_Domain_1.png)


#### Zscaler Admin Account:

After logging into your account, you will need to configure your Zscaler API roles and API admin account.  

For this Playbook to modify your Zscaler custom domain list, you will need a local Zscaler admin account that has access to the read and modify policy. To limit the access this account has to only what is needed, you will need to make a custom administrator role. 

In the Zscaler administration console hover over **Administration then click on Role Management**.

![Zscaler_Admin_Account_1](Images/Zscaler_Admin_Account_1.png)

Click on **Add Administrator Role**.

![Zscaler_Admin_Account_2](Images/Zscaler_Admin_Account_2.png)

Create a **Name** for the **Administrator Role** and use the settings **exactly** as depicted in the image below. Then click the **Save** button.

![Zscaler_Admin_Account_3](Images/Zscaler_Admin_Account_3.png)

Hover over the **Activation** button and click **Activate** to enable the new Role.

![Zscaler_Admin_Account_4](Images/Zscaler_Admin_Account_4.png)

Next, hover over **Administration** and click on **Administrator Management**.

![Zscaler_Admin_Account_5](Images/Zscaler_Admin_Account_5.png)

Click on **Add Administrator**.

![Zscaler_Admin_Account_6](Images/Zscaler_Admin_Account_6.png)

Enter a **Login ID** for the API administrator account you want to create. 

In the **Email** box you can enter a preexisting service account, or simply make up an email address which you will not use in your domain. There is no need for email access for this account.

Enter a name for the account and in the drop-down box below, select the Role you created in the previous step.

Make sure **Password Based Login** is checked and create a secure password for this API account.

Take note of the email address and password, as it will be needed during deployment.

![Zscaler_Admin_Account_7](Images/Zscaler_Admin_Account_7.png)

Click **Save**, then hover over the **Activation** button and click **Activate**. This will enable the new administrator account.

![Zscaler_Admin_Account_8](Images/Zscaler_Admin_Account_8.png)


#### Zscaler API Key:

To get your **API key** hover over the **Administration** button and click on **API Key Management**.

![Zscaler_API_Key_1](Images/Zscaler_API_Key_1.png)

Here you will find you **API Key** as well as **Zscaler Instance Name.** You will need both of these when deploying this playbook. The typical instance names are Zscaler, ZscalerOne, ZscalerTwo, ZscalerThree, and ZsCloud.

![Zscaler_API_Key_2](Images/Zscaler_API_Key_2.png)


#### Zscaler URL Category:

Lastly, you will need to note the custom URL category you want the domains from Microsoft Sentinel incidents added to. 

Hover over the **Administration** button and click on **URL Categories.** 

Take note of the name of your desired URL category, as it will be needed during deployment. 

![Zscaler_URL_Category_1](Images/Zscaler_URL_Category_1.png)

In the example below we use name of our Custom category AS_Blocklist. 
This category in our test environment configured to a Zscaler access policy that disallows users access to any domain in in that list.

![Zscaler_URL_Category_2](Images/Zscaler_URL_Category_2.png)


#### Create Azure Key Vault Secrets:

You will need to add you Zscaler API key and Zscaler password to an Azure key vault.

Navigate to the Azure key vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Select an existing key vault or create a new one. From the key vault overview page, click the "**Secrets**" menu option on the key vault page menu. Click "**Generate/Import**".

![Zscaler_Key_Vault_1](Images/Zscaler_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category-API-Key**” and enter the Zscaler API key copied previously in the "**Value**" field. All other settings can be left as is. Click "**Create**". 

![Zscaler_Key_Vault_2](Images/Zscaler_Key_Vault_2.png)

Repeat this process for your Zscaler password. 

![Zscaler_Key_Vault_3](Images/Zscaler_Key_Vault_3.png)

Once both secrets have been added to the vault, navigate to the "**Access policies**" menu option. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category#granting-access-to-azure-key-vault).

![Zscaler_Key_Vault_4](Images/Zscaler_Key_Vault_4.png)


#### Create an Integration Account:

You will need an integration account before this playbook can be deployed, as it is a requirement for executing JavaScript code, which is an operation used in the logic app.

Navigate to the Azure integration accounts page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Logic%2FintegrationAccounts

From the "**Overview**" page, select an existing integration account and take note of its name, or click "**Create**".

![Zscaler_Integration_Account_1](Images/Zscaler_Integration_Account_1.png)

Select the subscription and resource group that this playbook will be deployed to and a name for the integration account, such as "**AS-Zscaler-Integration**". Review the region and select a pricing tier, then click "**Review + create**".

![Zscaler_Integration_Account_2](Images/Zscaler_Integration_Account_2.png)

From the "**Review + create**" page, review the information, then click "**Create**".

![Zscaler_Integration_Account_3](Images/Zscaler_Integration_Account_3.png)

From the deployment page, take note of the resource name of your integration account, as it will be needed for deployment.

![Zscaler_Integration_Account_4](Images/Zscaler_Integration_Account_4.png)


#### Create Azure Blob Storage Container:

A blob storage file is needed for maintaining the Zscaler URL category values. Note the name and location of an existing one, or to create one, navigate to https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts

Create a storage account or select an existing one, then click the "**Containers**" menu option. Click the "**Container**" button and enter a name for the new container, such as "**zscaler-url-categories**", then click **Create**".

![Zscaler_Blob_Storage_1](Images/Zscaler_Blob_Storage_1.png)

Once your container has been created, you will need to upload a .csv file with the initial values of your Zscaler URL category. Click on your new container, then click "**Upload**" to open the dialogue box allowing you to upload your initial Zscaler URL category values in .csv format.

![Zscaler_Blob_Storage_2](Images/Zscaler_Blob_Storage_2.png)

You can easily view and edit the items in your file by clicking the ellipsis icon to the far right of the file and clicking "**View/edit**".

![Zscaler_Blob_Storage_3](Images/Zscaler_Blob_Storage_3.png)

Items can be added or removed on from the editable list. Once finished, click "**Save**".

![Zscaler_Blob_Storage_4](Images/Zscaler_Blob_Storage_4.png)

The logic app is set to run every 5 minutes polling this blob storage file for any changes. Because the logic app needs additional configuring after deployment, complete all deployment steps before testing any changes to this list, otherwise, time lapsed from now until then will likely put the last updated time outside of the polling window.


#
### Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:

Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category%2Fazuredeploy.json)

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:  
                                                  
* **Playbook Name**: This can be left as "**AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category**" or you may change it. 

* **Integration Account Name**: Enter the name of the Microsoft integration account this playbook will use. Please note that the playbook and integration account must share the same resource group.

* **Zscaler Root Domain**: Enter your Zscaler root domain here.

* **Zscaler Username**: Enter the username of the Zscaler Admin account. 

* **Zscaler Custom URL Category Name**: Enter a Zscaler Custom URL Category Name. 

* **Key Vault Name**: Enter the name of the Key Vault that stores your Zscaler API key and Zscaler password. 

* **Zscaler API Key**: Enter the name of the Key Vault Secret that contains the value of your Zscaler API key. 

* **Zscaler Password**: Enter the name of the Key Vault Secret that contains the value of your Zscaler password. 

Towards the bottom, click on “**Review + create**”. 

![Zscaler_Deploy_1](Images/Zscaler_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![Zscaler_Deploy_2](Images/Zscaler_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![Zscaler_Deploy_3](Images/Zscaler_Deploy_3.png)

Click on the “**Edit**” button. This will bring us into the Logic Apps Designer.

![Zscaler_Deploy_4](Images/Zscaler_Deploy_4.png)

Before the logic app can run successfully, some additional steps will need to be added. Click the "**+**" directly below the trigger labeled "**Recurrence**" and select "**Add an action**".

![Zscaler_Deploy_5](Images/Zscaler_Deploy_5.png)

Paste "**Blob**" into the search bar, and click the "**Get Blob Metadata (V2)**" action for "**Azure Blob Storage**".
                                                                                                
![Zscaler_Deploy_6](Images/Zscaler_Deploy_6.png)

You will be prompted to either create a connection to a storage container or select an existing one if it exists. Make sure the connection is for the storage container your Zscaler URL category values have been uploaded to. Next, click the file icon in the "**Blob**" field and select the folder containing your Zscaler URL categories file.

![Zscaler_Deploy_7](Images/Zscaler_Deploy_7.png)

After selecting the appropriate file, expand the ninth step labeled "**Condition**". Click in the input field with the placeholder "**Choose a value**" text. Select "**LastModified**" from the "**Dynamic content**" window.

![Zscaler_Deploy_8](Images/Zscaler_Deploy_8.png)

An additional step must be added after the second step in the true branch. Click the "**+**" directly below the step labeled "**Get Secret API Key**" and select "**Add an action**".

![Zscaler_Deploy_9](Images/Zscaler_Deploy_9.png)

Paste "**Blob**" into the search bar, and click the "**Get blob content (V2)**" action for "**Azure Blob Storage**".

![Zscaler_Deploy_10](Images/Zscaler_Deploy_10.png)

As previously done, select the proper connection and file for your Zscaler URL categories.

![Zscaler_Deploy_11](Images/Zscaler_Deploy_11.png)

Next, expand the step directly below labeled "**For each- URLs**" and click the function in the top field. In the dialogue box to the right, place your replace the two single quotes inside the **trim()**" function with the following: "**body('Get_blob_content_(V2)')**". Click "**Update**".

![Zscaler_Deploy_12](Images/Zscaler_Deploy_12.png)

Lastly, expand the step labeled "**Condition- URL parsing remove https protocol**". Click inside the input box and select "**Current item**" under "**For each - URLs**".

![Zscaler_Deploy_13](Images/Zscaler_Deploy_13.png)

Be sure to save the changes before exiting the logic app editor.


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the key vault connection created during deployment must be granted access to the key vault storing your Zscaler API key and password.

From the key vault "**Access policies**" page, click "**Create**".

![Zscaler_Access_1](Images/Zscaler_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![Zscaler_Access_2](Images/Zscaler_Access_2.png)

Paste "**AS-Blob-Storage-Add-Domains-to-Zscaler-URL-Category**" into the principal search box and click the option that appears. Click "**Next**" towards the bottom of the page.

![Zscaler_Access_3](Images/Zscaler_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![Zscaler_Access_4](Images/Zscaler_Access_4.png
