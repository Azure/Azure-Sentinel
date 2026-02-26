# AS-CrowdStrike-Alerts-Integration

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com    

This playbook will create a unidirectional integration with Microsoft Sentinel. It will pull CrowdStrike alerts (detections) into Microsoft Sentinel custom logs where they can be tracked and queried.

![CrowdStrike_Integration_Demo_1](Images/CrowdStrike_Integration_Demo_1.png)

> [!NOTE]  
> Estimated Time to Complete: 1 hour

> [!TIP]
> Required deployment variables are noted throughout. Reviewing the deployment page and filling out fields as you proceed is recommended.

#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* **CrowdStrike Domain** - the domain of the base URL indicated on the CrowdStrike OAuth client page. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Create-a-CrowdStrike-OAuth-Client)
* **CrowdStrike Client ID** - the Client ID the CrowdStrike OAuth client. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Create-a-CrowdStrike-OAuth-Client)
* **CrowdStrike API token** - the value of the API token generated for the CrowdStrike OAuth client. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Create-a-CrowdStrike-OAuth-Client)
* **Azure Key Vault Secret** - this will store the CrowdStrike API token. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#create-an-azure-key-vault-secret).
* **Sentinel Resource Name** - the name of the Log Analytics Workspace that the CrowdStrike logs will be sent to. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Log-Analytics-Workspace).
* **Sentinel Logs Workspace ID & Key** - the workspace ID and primary key of the Log Analytics Workspace that the CrowdStrike logs will be sent to. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Log-Analytics-Workspace).

> [!IMPORTANT]  
> Preexisting and recent alerts will need to be present in CrowdStrike in order to properly initialize the integration to Microsoft Sentinel

# 
### Setup

#### Create a CrowdStrike OAuth Client

From the home page of your CrowdStrike account, navigate to **Support and resources** in the left menu blade.
Click **Resources and tools** and then click **API Clients and Keys**.

![CrowdStrike_Integration_OAuth_1](Images/CrowdStrike_Integration_OAuth_1.png)

From the API client and Secrets page, click **Add new API Client**.

![CrowdStrike_Integration_OAuth_2](Images/CrowdStrike_Integration_OAuth_2.png)

Select the necessary API scopes and click **Save** to create the client.

![CrowdStrike_Integration_OAuth_3](Images/CrowdStrike_Integration_OAuth_3.png)

Locate the Client ID and Client Secret. Make sure to copy both of these items and save them somewhere that you can easily access later, as they will be needed for the deployment step.

![CrowdStrike_Integration_OAuth_4](Images/CrowdStrike_Integration_OAuth_4.png)

Select the Base URL for your region using the table below:

![CrowdStrike_Integration_OAuth_5](Images/CrowdStrike_Integration_OAuth_5.png)

Note the domain of the URL you selected, as it will be needed for the deployment step. It should follow this format "**api.example.CrowdStrike.com**".

#### Create an Azure Key Vault Secret

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults.

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![CrowdStrike_Integration_Key_Vault_1](Images/CrowdStrike_Integration_Key_Vault_1.png)

Choose a name for the secret, such as "**AS-CrowdStrike-Alerts-Integration-API-Token**", and enter the CrowdStrike API token copied previously in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Create-a-CrowdStrike-OAuth-Client). All other settings can be left as is. Click "**Create**". 

![CrowdStrike_Integration_Key_Vault_2](Images/CrowdStrike_Integration_Key_Vault_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option, also found under the "**Settings**" section on the Key Vault page menu. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#granting-access-to-azure-key-vault).

![CrowdStrike_Integration_Key_Vault_3](Images/CrowdStrike_Integration_Key_Vault_3.png)

#### Log Analytics Workspace

Navigate to the Log Analytics Workspace page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces.

Select the workspace that the CrowdStrike logs will be sent to, and take note of the name, as this will be needed for the deployment step.

![CrowdStrike_Integration_Log_Analytics_Workspace_1](Images/CrowdStrike_Integration_Log_Analytics_Workspace_1.png)

From the left menu blade, click **Agents** and expand the **Log Analytics agent instructions** section. Take note of both the workspace ID and primary key for a post deployment step.

![CrowdStrike_Integration_Log_Analytics_Workspace_2](Images/CrowdStrike_Integration_Log_Analytics_Workspace_2.png)

#
### Deployment

To configure and deploy this playbook:

Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-CrowdStrike-Alerts-Integration

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-CrowdStrike-Alerts-Integration%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-CrowdStrike-Alerts-Integration%2Fazuredeploy.json)

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.  
In the **Instance details** section:  
                                                  
* **Playbook Name**: This can be left as "**AS-CrowdStrike-Alerts-Integration**" or you may change it.

* **Client ID**: Enter the Client/ Token ID of your CrowdStrike API token referenced in [Create a CrowdStrike OAuth Client](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Create-a-CrowdStrike-OAuth-Client).

* **Key Vault Name**: Enter the name of the key vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#create-an-azure-key-vault-secret).

* **Secret Name**: Enter the name of the key vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#create-an-azure-key-vault-secret).

* **Sentinel Resource Name**: Enter the name of the Microsoft Sentinel Resource you will be sending the logs to referenced in [Log Analytics Workspace](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Log-Analytics-Workspace).

* **CrowdStrike Domain**: Enter the domain of the CrowdStrike base URL, following the format of 'api.CrowdStrike.com' referenced in [Create a CrowdStrike OAuth Client](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#Create-a-CrowdStrike-OAuth-Client).

Towards the bottom, click on "**Review + create**". 

![CrowdStrike_Integration_Deploy_1](Images/CrowdStrike_Integration_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![CrowdStrike_Integration_Deploy_2](Images/CrowdStrike_Integration_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![CrowdStrike_Integration_Deploy_3](Images/CrowdStrike_Integration_Deploy_3.png)

This Logic app is intentionally deployed as disabled. Complete the following steps before enabling.

#
### Granting Access to Azure Key Vault

Before the logic app should be enabled, the playbook must be granted access to the Key Vault storing your CrowdStrike API token.

From the Key Vault "**Access policies**" page, click "**Create**".

![CrowdStrike_Integration_Key_Vault_Access_1](Images/CrowdStrike_Integration_Key_Vault_Access_1.png)

Select the "**Get**" checkbox under "**Secret permissions**", then click "**Next**".

![CrowdStrike_Integration_Key_Vault_Access_2](Images/CrowdStrike_Integration_Key_Vault_Access_2.png)

Paste "**AS-CrowdStrike-Alerts-Integration**" into the principal search box and click the option that appears. Click "**Next**" towards the bottom of the page.

![CrowdStrike_Integration_Key_Vault_Access_3](Images/CrowdStrike_Integration_Key_Vault_Access_3.png)

Navigate to the "**Review + create**" section and click "**Create**".

![CrowdStrike_Integration_Key_Vault_Access_4](Images/CrowdStrike_Integration_Key_Vault_Access_4.png)

#
### Authorizing Playbook Connections

Before the logic app should be enabled, the **azureloganalyticsdatacollector** and **azuremonitorlogs** API connections will need to be edited and authorized.

From the playbook overview page, navigate to **API connections** from the left menu blade.

![CrowdStrike_Integration_API_Connections_1](Images/CrowdStrike_Integration_API_Connections_1.png)

Click the **azureloganalyticsdatacollector** connection and click **Edit API connection**. Enter in your Workspace ID and key, then click **Save**.

![CrowdStrike_Integration_API_Connections_2](Images/CrowdStrike_Integration_API_Connections_2.png)

Next, navigate back to the **API connections** page and click the **azuremonitorlogs** connection. Click **Edit API connection**, click **Authorize**, and then click **Save**.

![CrowdStrike_Integration_API_Connections_3](Images/CrowdStrike_Integration_API_Connections_3.png)

#
### Initial Run and Playbook configuration

This playbook runs every 5 minutes, collecting CrowdStrike alerts from the past 10 minutes to prevent data loss between executions. 
To avoid duplicate entries, the playbook checks incoming data against existing Sentinel logs. 
However, this check depends on a table that does not exist until the initial run creates it. 
To ensure successful table creation, the first run bypasses duplicate checking logic. 
After this run, the playbook must be **disabled**, necessary **"Run After" conditions updated**, and table population **verified**. 
Once confirmed, the playbook can be re-enabled to run normally.

To execute the initial run, **enable** the logic app. The trigger will run automatically.

![CrowdStrike_Integration_Initial_Run_1](Images/CrowdStrike_Integration_Initial_Run_1.png)

Click on the run and check for a successful **Send data** operation in the final step. Once you see this, **disable the logic app**. 

![CrowdStrike_Integration_Initial_Run_2](Images/CrowdStrike_Integration_Initial_Run_2.png)

![CrowdStrike_Integration_Initial_Run_3](Images/CrowdStrike_Integration_Initial_Run_3.png)

> [!NOTE]  
> If no data was returned for the 10 minute lookback window, allow the playbook to run until this condition is met. To expedite this, you can increase the lookback window by navigating to the **Logic app designer** adjusting the **addMinutes** function in the **HTTP - Get Alert IDs** step. The larger the negative number, the further the lookback. Be sure click **Update** if you change the formula, followed by **Save**.

![CrowdStrike_Integration_Initial_Run_4](Images/CrowdStrike_Integration_Initial_Run_4.png)

Once the Logic App has been disabled, navigate to the **Logic app designer** page and expand the last step labeled **Condition - Check for Results**.

![CrowdStrike_Integration_Initial_Run_5](Images/CrowdStrike_Integration_Initial_Run_5.png)

There are two steps that have a **Run after: has failed** checkbox that needs to be unchecked. 

Expand the step **For each - Sentinel Logs Alert IDs** and under settings, uncheck the **has failed** checkbox.

![CrowdStrike_Integration_Initial_Run_6](Images/CrowdStrike_Integration_Initial_Run_6.png)

Repeat this step for the **HTTP - Get Complete Alerts** step.

![CrowdStrike_Integration_Initial_Run_7](Images/CrowdStrike_Integration_Initial_Run_7.png)

Click **Save**.

![CrowdStrike_Integration_Initial_Run_8](Images/CrowdStrike_Integration_Initial_Run_8.png)

The [last section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Crowdstrike-Alerts-Integration#viewing-custom-logs) outlines how to view the custom logs to ensure they have been properly populated. After confirming the table has been created, go ahead and enable the Logic App.

![CrowdStrike_Integration_Initial_Run_9](Images/CrowdStrike_Integration_Initial_Run_9.png)

#
### Viewing Custom Logs

After the initial run has been completed, navigate to the Log Analytics Workspace page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces
From there, select the workspace your deployed logic apps reference and click "**Logs**" in the left-hand menu blade. Expand "**Custom Logs**". Here, you should see a table called **Crowdstrike_Alerts_CL**.
Note that it may take a while for this table to appear after it is created by the playbook, so if the logs are not yet visible, try querying them periodically.

![CrowdStrike_Integration_Custom_Logs_1](Images/CrowdStrike_Integration_Custom_Logs_1.png)
