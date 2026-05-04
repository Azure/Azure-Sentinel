<p align="center">
    <a href="#readme">
        <img alt="ANY.RUN logo" src="https://raw.githubusercontent.com/anyrun/anyrun-sdk/b3dfde1d3aa018d0a1c3b5d0fa8aaa652e80d883/static/logo.svg">
    </a>
</p>

______________________________________________________________________

# ANY.RUN Malware Sandbox Integration with Microsoft Sentinel 

## Overview

This solution folder contains resources required for integrating Microsoft Sentinel with ANY.RUN Sandbox. 

The connectors enrich Microsoft Sentinel incidents by analyzing URLs or files associated with them in the sandbox. As a result, your Microsoft Sentinel incidents will include detailed info on threats. You will also be able to explore the object's behavior in a real infrastructure environment. 

Additionally, your Threat Intelligence portal in Sentinel will be enriched with Indicators of Compromise (IOCs) extracted during the sandbox analysis. You can try out the connectors for free by [getting 14-day trial](https://any.run/demo/?utm_source=anyrungithub&utm_medium=documentation&utm_campaign=sentinel&utm_content=linktodemo) of ANY.RUN Sandbox’s Enterprise plan. 

## Integration capabilities

- Enrichment of incidents with:
  - Analysis verdict (malicious, suspicious, unknown) 
  - Threat score (from 0 to 100) 
  - Malware tags (e.g. threat family) 
  - Table with IOC's detected during the analysis 
  - Link to the analysis session in the sandbox 
- Uploading IOC's detected during the analysis to Sentinel Threat Intelligence portal 

## Analyze URLs from Microsoft Sentinel Incidents via ANY.RUN Sandbox

**Latest Version:** 1.0.0  
**Release Date:** 10/09/2025

This playbook extracts URLs from incidents and submits them for analysis in ANY.RUN Sandbox to enrich the incident with a verdict using a single Azure Logic App.

[Open connector's page](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Sandbox-URL)

## Analyze Files from Microsoft Sentinel Incidents via ANY.RUN Sandbox

**Latest Version:** 1.0.1  
**Release Date:** 25/09/2025

This playbook allows you to send files from incidents for analysis in ANY.RUN Sandbox. It uploads the file from the endpoint to Azure Blob Storage and then forwards it to ANY.RUN Sandbox using Azure Logic App and Azure Function App.

Templates are provided for endpoints running the following operating systems:
- Windows
- Ubuntu
- Debian

[Open Playbooks folder](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks)

## Analyze All Entities from Microsoft Sentinel Incidents via ANY.RUN Sandbox and Microsoft Defender for Endpoint

**Latest Version:** 1.0.1  
**Release Date:** 25/09/2025

This playbook makes the incident enrichment process in Microsoft Sentinel even more automated if you are also using Microsoft Defender for Endpoint (MDE). In this case, the entire automation mechanism can be combined into Azure Logic App and Azure Function App, leveraging MDE's capabilities to extract files from endpoints via API.

[Open connector's page](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Sandbox-File-Defender)

## Prerequisites

### Key Vault

- You need the Enterprise pricing plan in ANY.RUN and your API key. We recommend storing your API key in Azure Key Vault. To do this, select your existing Key Vault or create a new one. Then, navigate to the **Objects** > **Secrets** section and create a new secret named `ANYRUN-APIKey`.

  > **Note:** It is recommended to keep this name unchanged. Otherwise, you will need to update it later in the deployed Logic App.

![key_vault](Images/001.png)

### App Registration

- You need to create a new application for your connector. To do this, go to **Microsoft Entra ID**.

![entra_id](Images/002.png)

- Click **Add** > **App registration**.

![app_registration](Images/003.png)

- Name your new application and click **Register**.

![register_app](Images/004.png)

### Secret Value of created App

- To generate the Client Secret, go to your application's page and click **Generate Secret** in the **Certificates & secrets** tab.

![cert_and_secrets_tab](Images/040.png)

- Specify the key name and its expiration date (optional).

![generate_secret](Images/041.png)

- Copy and **save the Secret Value**. This value is required for deploying the connector later.

### API Permissions for new App

#### Key Vault API Permissions

- Go this tab: **Manage** > **API permissions**. Click Add a permission and choose the following options: 

![add_permission](Images/007.png)

- In the **Microsoft APIs** tab, add **Azure Key Vault**.

![add_vault_permission](Images/005.png)

- Add the following permissions for it:

| Category | Permission Name   | Description                                                                 |
|----------|-------------------|-----------------------------------------------------------------------------|
| N/A      | user_impersonation | Allow the application full access to the Azure Key Vault service on behalf of the signed-in user |

#### Microsoft Defender ATP API Permissions

  > **Note:** This section is only required if you use Microsoft Defender for Endpoint (MDE) to extract files from the endpoint.

- Add an API connection for **WindowsDefenderATP**. Select the corresponding API in the **APIs my organization uses** tab.

![select_defender_permission](Images/008.png)

- Then, select **Application permissions**.

![add_defender_permission](Images/009.png)

- Select the following permissions:

| Category | Permission Name    | Description                                                                 |
|----------|--------------------|-----------------------------------------------------------------------------|
| Machine  | Machine.LiveResponse | Needed to gather evidences from machines                                  |
| Machine  | Machine.Read.All   | Needed to retrieve information about machines                               |
| Library  | Library.Manage     | Needed to upload custom ps1 script for retrieving AV related evidences      |

### Required Roles for the New App

#### Key Vault

- Navigate to the required Key Vault where you previously added the ANY.RUN API-Key.

![kv_role_overview](Images/018.png)

- Open **Access control (IAM)** > **Add** > **Add role assignment**.

![kv_role_add](Images/019.png)

- In the search window, type and select the role **Key Vault Secrets User**, then click **Next**.

![kv_role_search](Images/020.png)

- Description of the required role:

| Name                   | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| Key Vault Secrets User | Read secret contents. Only works for key vaults that use the 'Azure role-based access control' permission model. |

- Then, assign this role to the created application **ANYRUN-App**.

![kv_role_select](Images/021.png)

#### Sentinel

- Open your Sentinel workspace and navigate to **Settings** > **Workspace settings**.

![sentinel_settings](Images/022.png)

- Open **Access control (IAM)** > **Add** > **Add role assignment**.

![sentinel_role_add](Images/023.png)

- In the search window, type and select the roles **Microsoft Sentinel Contributor** and **Log Analytics Contributor**, then click **Next**.

![sentinel_role_search](Images/024.png)

- Description of the required roles:

| Name                         | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| Microsoft Sentinel Contributor | Microsoft Sentinel Contributor                                              |
| Log Analytics Contributor    | Log Analytics Contributor can read all monitoring data and edit monitoring settings. Editing monitoring settings includes adding the VM extension to VMs; reading storage account keys to be able to configure collection of logs from Azure Storage; adding solutions; and configuring Azure diagnostics on all Azure resources. |

- Then, assign these roles to the created application **ANYRUN-App**.

![sentinel_role_select](Images/025.png)

### Storage Account

  > **Note:** This section is only required for workflows where you use Azure Blob Storage to store files from the endpoint before submitting it to ANY.RUN Sandbox.

- Go to Azure Storage Accounts.

![azure_sa](Images/010.png)

- Click **Create**.

![azure_sa_create](Images/011.png)

- Type the name of Storage Account and click **Review + Create**.

![azure_sa_review_and_create](Images/012.png)

- Open your Storage Account and go to **Access Control (IAM)** > **Add**.

![sa_iam_add](Images/013.png)

- Select your app — `ANYRUN-App`.

![sa_app_select](Images/014.png)

- Find the following roles:

![sa_role_find](Images/015.png)

| Role                          | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| Storage Account Contributor   | Lets you manage storage accounts, including accessing storage account keys which provide full access to storage account data. |
| Storage Blob Data Contributor | Allows for read, write and delete access to Azure Storage blob containers and data. |

- Open your Storage Account. Go to **Data Storage** > **Containers**.

![sa_navigation](Images/016.png)

- Click **Add container**, enter its name and click **Create**.

![sa_container_create](Images/017.png)

- Go to **Security + networking** > **Access keys**, copy and save **Key** and **Connection string**. These values are required for deploying the connector later.

![sa_key](Images/043.png)

## Deployment

### Deploy Azure Function App

> **Note:** This section is only required for workflows with file analysis (Sandbox-File-*, Sandbox-File-Defender).

- Click below to deploy Azure Function App with **Flex Consumption plan**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSentinel-FA%2Fazuredeploy.json)

- Enter the parameters required for deploying the Function App and click **Review + create**.

![function_app_deployment](Images/081.png)

- Description of the required parameters:

| Parameter Name               | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| functionAppName              | Workflow name.                                                              |
| AzureStorageAccountName      | Azure Blob Storage Account Name.                                            |
| AzureStorageConnectionString | Azure Blob Storage Account Connection string.                               |
| LogAnalyticsWorkspaceName    | Log Analytics Workspace Name.                                               |

### Deploy Azure Logic Apps App

#### 1. Analyze URLs from Microsoft Sentinel Incidents via ANY.RUN Sandbox (Sandbox-URL)

##### Microsoft Sentinel Connector for automated URL analysis via ANY.RUN's Malware Sandbox

###### Overview

This playbook extracts URLs from incidents and submits them for analysis in ANY.RUN Sandbox to enrich the incident with a verdict using a single Azure Logic App.

###### Requirements

* ANY.RUN API-Key
* Microsoft Sentinel
* Azure Logic App (Flex Consumption plan)

###### Deployment

Click below to deploy Azure Logic App with **Flex Consumption plan**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSandbox-URL%2Fazuredeploy.json)

Enter the parameters required for deploying the Logic App and click **Review + create**.

![logic_app_deployment](Images/URL_004.png)

Description of the required parameters:

| Parameter Name | Description |
| --- | --- |
| LogicAppName | Workflow name. |
| AzureTenantId | Tenant ID for authentication in connections. |
| AzureClientId | Client ID for authentication (ID of the App Registration created before). |
| azureClientSecret | Client Secret for authentication. |
| keyVaultName | Key Vault name. |
| keyVaultUri | Key Vault URI (copy Vault URI from your Key Vault overview). |

###### Logic App configuration (Optional)

###### ANY.RUN Sandbox analysis parameters

ANY.RUN is an interactive online malware analysis service for dynamic and static research of most types of threats using a customizable VM environment. We offer a connector for Microsoft Sentinel, which you can independently adapt to your infrastructure and needs in just a few clicks. You can easily change the parameters used for analyzing the required URL.

> Note:  
> You can learn more about the capabilities of ANY.RUN Sandbox by reviewing our [API documentation](https://any.run/api/docs).

The main setup and customization of the Logic App is available through the graphical editor (**Development tools** > **Logic app designer**) or the code editor (**Development tools** > **Logic app code view**).

The URL analysis parameters in ANY.RUN Sandbox are defined in the **HTTP-RunNewURLAnalysis** action.

![analysis_action](Images/URL_001.png)

Analysis options are specified in the HTTP request body.

![analysis_parameters](Images/URL_002.png)

Description of the default parameters:

| Parameter Name | Description |
| --- | --- |
| obj_type | Specifies the type of the new task (the value "url" is required for this workflow). |
| opt_timeout | Defines the timeout option for the analysis. |
| obj_ext_browser | Indicates the browser name to use. |
| env_os | Specifies the operating system. |
| env_bitness | Defines the bitness of the operating system. |
| env_version | Sets the version of the operating system. |
| opt_automated_interactivity | Controls the automated interactivity (ML) option (changing this is not recommended). |
| auto_confirm_uac | Enables automatic confirmation of Windows UAC requests (changing this is not recommended). |

> Note:  
> You can add more parameters for analysis. To see the full list of available parameters and their values, visit our [API documentation](https://any.run/api/docs).

###### Simultaneous Analysis of Objects in ANY.RUN Sandbox

ANY.RUN Sandbox allows users to perform multiple analyses simultaneously (availability and capability depend on your pricing plan). By default, if a Microsoft Sentinel incident contains multiple URLs, each analysis will run sequentially (a new URL analysis won't start until the previous one is finished).

To increase the speed of incident enrichment, you can analyze objects simultaneously. To do this, go to `For each - URL` loop > `Settings` and increase the `Degree of parallelism` value. Note that you should set a value that does not exceed the number of parallel analyses available at your pricing plan.

![parallel_analysis](Images/URL_003.png)

> Note:  
> To upgrade your pricing plan capabilities, [contact us](https://app.any.run/contact-us/).

#### 2. Analyze Files from Microsoft Sentinel Incidents via ANY.RUN Sandbox (Sandbox-File)

##### Microsoft Sentinel Connector for automated File analysis via ANY.RUN's Malware Sandbox

###### Overview

> Note:  
> If you are using the Microsoft Sentinel & Microsoft Defender for Endpoint bundle in your infrastructure, we strongly recommend using the [corresponding connector](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Sandbox-File-Defender) for this case.

This playbook allows you to send files from incidents for analysis in the ANY.RUN Sandbox. It uploads the file from the endpoint to Azure Blob Storage and then forwards it to ANY.RUN Sandbox using Azure Logic App and Azure Function App.

Templates are provided for endpoints running the following operating systems:

* Windows
* UNIX (Ubuntu, Debian)

###### Requirements

* ANY.RUN API-Key
* Microsoft Sentinel
* Azure Logic App (Flex Consumption plan)
* Azure Function App (Flex Consumption plan)
* Azure Blob Storage
* Microsoft Defender for Endpoint (**Optional**)

###### Solution overview

The connector consists of two Azure Logic Apps:

* **Parent workflow** (varies depending on the host operating system):
  * [ANYRUN-Sandbox-File-Windows](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Sandbox-File-Windows)
  * [ANYRUN-Sandbox-File-Ubuntu](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Sandbox-File-Ubuntu)
  * [ANYRUN-Sandbox-File-Debian](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Sandbox-File-Debian)
* **Child workflow** (uniform for all operating systems):
  * [ANYRUN-Submit-File-to-Blob](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANY.RUN/Playbooks/Submit-File-to-Blob)

###### Logic Apps description

**Parent Workflow**  
This Logic App serves as the main orchestration workflow for the connector. It is triggered by a Microsoft Sentinel incident webhook and processes file entities associated with the incident. The workflow submits files for analysis in ANY.RUN Sandbox obtained from Azure Blob Storage.

**Child Workflow**  
This Logic App is a child workflow invoked by the parent to handle file upload from hosts to Azure Blob Storage using Microsoft Defender for Endpoint. It is triggered by an HTTP request from the parent and parses input data. For each file, it initiates MDE live response to execute a script on the host for upload file to Azure Blob Storage.

> Note:  
> The child playbook in this connector is designed to extract files from the endpoint and upload them to Azure Blob Storage using Microsoft Defender for Endpoint (MDE). If you use a different solution instead of MDE, you can replace this playbook with one adapted for your infrastructure.

###### Deployment

**Child Logic App**  
First, you need to deploy the child Logic App, as its parameters are required for configuring the parent one.

Click below to deploy Child Azure Logic App with **Flex Consumption plan**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSubmit-File-to-Blob%2Fazuredeploy.json)

![child_logic_app_deployment](Images/File_004.png)

Enter the parameters required for deploying the Logic App and click **Review + create**.

Description of the required parameters:

| Parameter Name | Description |
| --- | --- |
| LogicAppName | Workflow name. |
| AzureTenantId | Tenant ID for authentication in connections. |
| AzureClientId | Client ID for authentication (ID of the App Registration created before). |
| azureClientSecret | Client Secret for authentication. |
| logAnalyticsWorkspaceName | Log Analytics Workspace Name. |

**Parent Logic App**  
You can deploy all the proposed parent Logic Apps or select specific ones depending on the operating system installed on your endpoints. The parent Logic Apps operate independently of each other.

Click below to deploy Parent Azure Logic App with **Flex Consumption plan**

* ANYRUN-Sandbox-File-Windows  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSandbox-File-Windows%2Fazuredeploy.json)
* ANYRUN-Sandbox-File-Ubuntu  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSandbox-File-Ubuntu%2Fazuredeploy.json)
* ANYRUN-Sandbox-File-Debian  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSandbox-File-Debian%2Fazuredeploy.json)

![parent_logic_app_deployment](Images/File_015.png)

Enter the parameters required for deploying the Logic App and click **Review + create**.

Description of the required parameters:

| Parameter Name | Description |
| --- | --- |
| logicAppName | Workflow name. |
| azureTenantId | Azure Tenant ID for authentication. |
| azureClientId | Azure Client ID for authentication. |
| azureClientSecret | Azure Client Secret for authentication. |
| keyVaultName | Key Vault name. |
| keyVaultUri | Key Vault URI. |
| azureBlobStorageAccountName | Azure Blob Storage Account Name. |
| azureBlobStorageConnectionString | Azure Blob Storage Connection String. |
| azureBlobStorageContainerName | Azure Blob Storage Container Name. |
| childWorkflowName | Name of the child Logic App (deployed before). |
| functionAppName | Name of the Function App to call (deployed before). |

###### Storage Account Configuration

To generate an SAS token for Azure Blob Storage, you need to assign the appropriate role directly to the Logic App.

Open your Storage Account.  
Navigate to **Access Control (IAM)** and click **Add**.

![storage_child_logic_app](Images/File_006.png)

Specify the child Logic App `ANYRUN-Submit-File-to-Blob`.  
Select the following role:

| Name | Description |
| --- | --- |
| Storage Account Contributor | Lets you manage storage accounts, including accessing storage account keys which provide full access to storage account data. |

###### Logic App configuration (Optional)

###### ANY.RUN Sandbox analysis parameters

ANY.RUN is an interactive online malware analysis service for dynamic and static research of most types of threats using a customizable VM environment. We offer a connector for Microsoft Sentinel, which you can independently adapt to your infrastructure and needs in just a few clicks. You can easily change the parameters used for analyzing the required file.

> Note:  
> You can learn more about the capabilities of ANY.RUN Sandbox by reviewing our [API documentation](https://any.run/api/docs).

The main setup and customization of the Logic App is available through the graphical editor (**Development tools** > **Logic app designer**) or the code editor (**Development tools** > **Logic app code view**).

For File analysis — in the following three actions which are responsible for declaring the parameters:
* ANY.RUN general analysis options
* ANY.RUN Windows analysis options
* ANY.RUN Linux analysis options

In the ANY.RUN general analysis options action, you can modify parameters that define general, OS-independent options such as analysis duration, virtual machine network settings, privacy, and more.  
In the ANY.RUN Windows analysis options and ANY.RUN Linux analysis options actions, you can modify parameters that affect OS-specific virtual machine settings.

Description of the main parameters:

| Parameter Name | Description |
| --- | --- |
| opt_timeout | Defines the timeout option for the analysis. |
| env_os | Specifies the operating system. |
| env_bitness | Defines the bitness of the operating system. |
| env_version | Sets the version of the operating system. |
| env_type | Specify the environment preset type. |
| opt_automated_interactivity | Controls the automated interactivity (ML) option (changing this is not recommended). |
| auto_confirm_uac | Enables automatic confirmation of Windows UAC requests (changing this is not recommended). |
| run_as_root | Allow the file to run with superuser privileges on Linux. |
| obj_ext_extension | Specify whether to change the file extension to a valid one. |

###### Simultaneous Analysis of Objects in ANY.RUN Sandbox

ANY.RUN Sandbox allows users to perform multiple analyses simultaneously (availability and capability depend on your pricing plan). By default, if a Microsoft Sentinel incident contains multiple files, each analysis will run sequentially.

To increase the speed of incident enrichment, you can analyze objects simultaneously. To do this, open `For each - detonate files to ANY.RUN Sandbox` loop > `Settings` and increase the `Degree of parallelism` value.

> Note:  
> To expand your capabilities by upgrading your pricing plan, [contact us](https://app.any.run/contact-us/).

#### 3. Analyze All Entities via ANY.RUN Sandbox and Microsoft Defender for Endpoint (Sandbox-File-Defender)

##### ANY.RUN Malware Sandbox Integration with Microsoft Sentinel and Defender for Endpoint for automated file and URL analysis

###### Overview

This template makes the incident enrichment process in Microsoft Sentinel even more automated if you are also using Microsoft Defender for Endpoint (MDE).  
In this case, the entire automation mechanism can be combined into Azure Logic App and Azure Function App, leveraging MDE's capabilities to extract files from UNIX- or Windows-endpoints using the bash and PowerShell script we offer.

This Logic App allows you to send URLs and files contained in the incident entities for analysis in ANY.RUN Sandbox. The playbook enables initiating Live Response sessions to hosts connected to Microsoft Defender for Endpoint. Within these Live Response sessions, a script is launched that extracts files from the endpoint and sends them for temporary storage to an Azure Blob Storage container. Once the file arrives in Blob Storage, the Logic App retrieves it and forwards it for analysis to ANY.RUN API.

After the analysis is completed in ANY.RUN Sandbox, its key results (verdict, score, and tags) enrich the incident. They help you obtain more detailed information on your sample. Additionally, IOCs discovered during the analysis in ANY.RUN Sandbox will be added to the Sentinel TI Portal.

###### Requirements

* ANY.RUN API-Key
* Microsoft Sentinel
* Azure Logic App (Flex Consumption plan)
* Azure Function App (Flex Consumption plan)
* Azure Blob Storage
* Microsoft Defender for Endpoint

###### Deployment

Click below to deploy Azure Logic App with **Flex Consumption plan**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FANY.RUN%2FPlaybooks%2FSandbox-File-Defender%2Fazuredeploy.json)

![logic_app_deployment](Images/Defender_011.png)

Enter the parameters required for deploying the Logic App.

Description of the required parameters:

| Parameter Name | Description |
| --- | --- |
| logicAppName | Workflow Name. |
| azureTenantId | Azure Tenant ID for authentication. |
| azureClientId | Azure Client ID for authentication. |
| azureClientSecret | Azure Client Secret for authentication. |
| keyVaultName | Key Vault name. |
| keyVaultUri | Key Vault URI. |
| azureBlobStorageAccountName | Azure Blob Storage Account Name. |
| azureBlobStorageConnectionString | Azure Blob Storage Connection String. |
| azureBlobStorageContainerName | Azure Blob Storage Container Name. |
| logAnalyticsWorkspaceName | Log Analytics Workspace Name. |
| functionAppName | Name of the Function App to call (deployed before). |

###### Storage Account Configuration

To generate an SAS token for Azure Blob Storage, you need to assign the appropriate role directly to the Logic App.

Open your Storage Account.  
Navigate to **Access Control (IAM)** and click **Add**.

![storage_logic_app](Images/Defender_010.png)

Specify the Logic App `ANYRUN-Sandbox-Defender`.  
Select the following role:

| Name | Description |
| --- | --- |
| Storage Account Contributor | Lets you manage storage accounts, including accessing storage account keys which provide full access to storage account data. |

###### Microsoft Defender for Endpoint configuration and additional script

> Note:  
> To allow the connector to extract all files of interest from endpoints (including potentially dangerous ones), we recommend setting **Quarantine** as the default action for your MDE.

**Enable Live Response Sessions**  
Open your [MDE portal](https://security.microsoft.com).  
Navigate to **System** > **Settings** > **Endpoints** > **General** > **Advanced features**.  
Enable the following settings: **Live Response**, **Live Response for Servers**, and **Live Response unsigned script execution**.

![enable_live_response](Images/Defender_002.png)

**Upload Helper Scripts to the Local Library of Your Endpoints**  
Open your MDE portal.  
Navigate to **Assets** > **Devices**.  
Open the required device.  
Click on `...` in the upper right corner and then **Initiate Live Response Session**.

![run_live_response](Images/Defender_003.png)

Click **Upload file to library**.

![click_upload_file](Images/Defender_004.png)

Click **Upload file to library** again, select the script from your file system (after downloading it from our [library](https://github.com/rollehfoh/ANY.RUN/tree/main/scripts)), or create your own script. After that, click **Submit**.

![select_file_to_upload](Images/Defender_005.png)

###### Logic App configuration (Optional)

###### ANY.RUN Sandbox analysis parameters

The analysis parameters in ANY.RUN Sandbox are defined in the actions of the deployed Logic App.

For URL analysis — **HTTP-RunNewURLAnalysis**  
For File analysis — in the following three actions:
* ANY.RUN general analysis options
* ANY.RUN Windows analysis options
* ANY.RUN Linux analysis options

Description of the main parameters:

| Parameter Name | Description |
| --- | --- |
| opt_timeout | Defines the timeout option for the analysis. |
| env_os | Specifies the operating system. |
| env_bitness | Defines the bitness of the operating system. |
| env_version | Sets the version of the operating system. |
| env_type | Specify the environment preset type. |
| opt_automated_interactivity | Controls the automated interactivity (ML) option (changing this is not recommended). |
| auto_confirm_uac | Enables automatic confirmation of Windows UAC requests (changing this is not recommended). |
| run_as_root | Allow the file to run with superuser privileges on Linux. |
| obj_ext_extension | Specify whether to change the file extension to a valid one. |

###### Simultaneous Analysis of Objects in ANY.RUN Sandbox

ANY.RUN Sandbox allows users to perform multiple analyses simultaneously (availability and capability depend on your pricing plan). By default, if a Microsoft Sentinel incident contains multiple files, each analysis will run sequentially.

To increase the speed of incident enrichment, you can analyze objects simultaneously. To do this, open `For each - URLs` and `For each - detonate files to ANY.RUN Sandbox` loop > `Settings` and increase the `Degree of parallelism` value.

> Note:  
> To expand your capabilities by upgrading your pricing plan, [contact us](https://app.any.run/contact-us/).

## Request Support or Access to ANY.RUN’s Products

Feel free to reach out to us for sales, demo, or quote inquiries via the [contact us form](https://app.any.run/contact-us/?utm_source=anyrungithub&utm_medium=documentation&utm_campaign=sentinel&utm_content=linktocontactus) or write to [techsupport@any.run](mailto:techsupport@any.run) for technical assistance.
