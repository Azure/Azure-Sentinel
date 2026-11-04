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

[Open connector's page](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANYRUN/Playbooks/Sandbox-URL)

## Analyze Files from Microsoft Sentinel Incidents via ANY.RUN Sandbox

**Latest Version:** 1.0.1  
**Release Date:** 25/09/2025

This playbook allows you to send files from incidents for analysis in ANY.RUN Sandbox. It uploads the file from the endpoint to Azure Blob Storage and then forwards it to ANY.RUN Sandbox using Azure Logic App and Azure Function App.

Templates are provided for endpoints running the following operating systems:
- Windows
- Ubuntu
- Debian

[Open Playbooks folder](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANYRUN/Playbooks)

## Analyze All Entities from Microsoft Sentinel Incidents via ANY.RUN Sandbox and Microsoft Defender for Endpoint

**Latest Version:** 1.0.1  
**Release Date:** 25/09/2025

This playbook makes the incident enrichment process in Microsoft Sentinel even more automated if you are also using Microsoft Defender for Endpoint (MDE). In this case, the entire automation mechanism can be combined into Azure Logic App and Azure Function App, leveraging MDE's capabilities to extract files from endpoints via API.

[Open connector's page](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/ANYRUN/Playbooks/Sandbox-File-Defender)

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

Deploy the components in the following order. Shared prerequisites (Key Vault secret `ANYRUN-APIKey`, App Registration, API permissions, role assignments, and Storage Account) are described in the [Prerequisites](#prerequisites) section above.

1. Deploy the Function App (`ANYRUN-Sentinel-FA`) if you plan to analyze files.  
   Detailed steps: [Playbooks/Sentinel-FA/README.md](Playbooks/Sentinel-FA/README.md)

2. Deploy the child playbook `Submit-File-to-Blob` only if you need to analyze files **and** you are **not** using Microsoft Defender for Endpoint (MDE) to collect files from endpoints. It is not required for URL-only analysis or when using the Defender playbook.  
   Detailed steps: [Playbooks/Submit-File-to-Blob/README.md](Playbooks/Submit-File-to-Blob/README.md)

3. Deploy one or more of the following playbooks. Each has its own readme with the Deploy button, parameters, post-deployment steps, and screenshots:

   - **Sandbox-URL** — analyze URL entities.  
     [Playbooks/Sandbox-URL/README.md](Playbooks/Sandbox-URL/README.md)

   - **Sandbox-File-Defender** — analyze files and URLs using Microsoft Defender for Endpoint Live Response. Use this playbook if MDE is available.  
     [Playbooks/Sandbox-File-Defender/README.md](Playbooks/Sandbox-File-Defender/README.md)

   - **Sandbox-File-Windows** — analyze files from Windows endpoints (use only if MDE is not available).  
     [Playbooks/Sandbox-File-Windows/README.md](Playbooks/Sandbox-File-Windows/README.md)

   - **Sandbox-File-Ubuntu** — analyze files from Ubuntu endpoints (use only if MDE is not available).  
     [Playbooks/Sandbox-File-Ubuntu/README.md](Playbooks/Sandbox-File-Ubuntu/README.md)

   - **Sandbox-File-Debian** — analyze files from Debian endpoints (use only if MDE is not available).  
     [Playbooks/Sandbox-File-Debian/README.md](Playbooks/Sandbox-File-Debian/README.md)

After deploying a playbook, authorize its API connections, assign the required roles to the managed identity, and create an Automation Rule in Microsoft Sentinel. Playbook-specific notes are in the corresponding `README.md`.

## Request Support or Access to ANY.RUN’s Products

Feel free to reach out to us for sales, demo, or quote inquiries via the [contact us form](https://app.any.run/contact-us/?utm_source=anyrungithub&utm_medium=documentation&utm_campaign=sentinel&utm_content=linktocontactus) or write to [techsupport@any.run](mailto:techsupport@any.run) for technical assistance.
