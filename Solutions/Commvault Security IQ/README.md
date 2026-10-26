Commvault Security IQ - Microsoft Sentinel Integration
======================================================

This integration connects Commvault Cloud with Microsoft Sentinel to enable anomaly ingestion, incident creation, investigation, and response through analytic rules, playbooks, and the Commvault Security Investigation Agent.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Required Azure Resources](#required-azure-resources)
- [Installation](#installation)
- [Using Commvault Security Investigation Agent](#using-commvault-security-investigation-agent)
- [Automation Account and Runbooks Setup](#automation-account-and-runbooks-setup)
- [Support](#support)

## Overview
This solution provides:
- **Data Ingestion**: Automated collection of Commvault client anomaly events via the Codeless Connector Framework
- **Incident Creation**: Creation of Microsoft Sentinel incidents from Commvault anomaly detections after the analytic rule is created and enabled
- **AI-powered Insights**: Use the Commvault Security Investigation Agent in Microsoft Security Copilot to correlate Commvault anomaly events with signals from tools such as CrowdStrike, Netskope, and Palo Alto to validate impact on affected hosts and speed investigation
- **Incident Response**: Playbook templates for remediation actions such as disabling users, disabling SAML identity providers, and disabling data aging

## Prerequisites
Before beginning the installation, ensure you have:

### Commvault Requirements
- **Administrative Access**: Admin or Tenant Admin privileges in Commvault Cloud/Metallic
- **API Access**: Ability to generate access tokens for API integration

### Azure Requirements
- **Subscription Access**: Contributor or Owner permissions on the Azure subscription
- **Resource Group Access**: Ability to create and manage resources in the target resource group
- **Microsoft Sentinel**: An active Sentinel workspace deployed in your Azure environment
- **Log Analytics Workspace**: A Log Analytics workspace associated with your Sentinel instance
- **Azure Cloud Shell**: Access to Azure Cloud Shell with PowerShell support
- **Response automation resources**: A Key Vault and an Automation Account are required only if you deploy and use the included incident response playbooks

## Required Azure Resources

The **Commvault Security IQ (via Codeless Connector Framework)** data connector collects Commvault anomaly events in Microsoft Sentinel. After you connect the connector, events are available in the `CommvaultAlertsCCF_CL` table.

After you select **Add connector** and click **Connect**, Microsoft Sentinel creates the connector resources and starts polling the Commvault API.

The included response playbooks have separate prerequisites: they use an Azure Key Vault to retrieve Commvault credentials and an Azure Automation Account to run the remediation runbooks. These resources are not required for CCF data ingestion.

If you use the response playbooks, create the following secrets in the Key Vault that you provide during playbook deployment:
- `access-token`: The Commvault API token
- `environment-endpoint-url`: The Commvault API base URL, including `/commandcenter/api`

## Installation

1. **Create an API token in Commvault:**

   - Follow the instructions in [Creating an Access Token](https://documentation.commvault.com/2024e/essential/creating_access_token.html).
   - Ensure the user creating the token has **Admin** or **Tenant Admin** privileges.
   - Copy the generated **API token**; you will need it in step 4.

> **Important — Token Expiry:** API tokens expire after **120 minutes** by default. Since the CCF connector stores the token as a static credential with no automatic refresh, the connector will stop ingesting data once the token expires. To avoid this, increase the token expiry **before** generating the token:
> 1. In Commvault Command Center, go to **Manage** > **Company** and select your company.
> 2. On the **Overview** tab, scroll down to the **Settings** tile and click **Add**.
> 3. In the **Name** box, enter `AccessTokenExpiryInMinutes`. Set **Category** to `CommServDB.Console` and **Type** to `Integer`.
> 4. In the **Value** box, enter `43200` (30 days) or your preferred duration in minutes (max: `43200`).
> 5. Click **Save**, then generate the API token — the new expiry will apply.

2. **Install the Commvault Security IQ solution:**

   - In Microsoft Sentinel, open **Content hub**, search for **Commvault Security IQ**, and select **Install**.

3. **Open the CCF data connector:**

   - In Microsoft Sentinel, open **Data connectors**, search for **Commvault Security IQ (via Codeless Connector Framework)**, and open the connector page.

4. **Configure the connection:**

    - Under **Configuration**, enter the following:
       - **Commvault Environment Endpoint URL**: Your Commvault Cloud API base URL including the `/commandcenter/api` path (for example, `https://your-commvault-endpoint/commandcenter/api`).
       - **API token**: The API token generated in step 1.
    - Click **Connect**.

The connector polls Commvault every 30 minutes and ingests threat anomaly events into the `CommvaultAlertsCCF_CL` table in your Log Analytics workspace.

### Incident Detection and Response Setup Steps

5. **Create and enable the analytic rule:**

   - In **Content hub**, open **Commvault Security IQ** -> **Manage** -> **Commvault Cloud Alert** -> **Create Rule** -> **Next** -> **Save**.
   - Enable the rule after confirming that data is available in `CommvaultAlertsCCF_CL`.

6. **Create the response playbooks:**

   - In **Content hub**, open **Commvault Security IQ** -> **Manage**, select a playbook, and choose **Configuration** -> **Create Playbook** -> **Next** -> **Create**.
   - Repeat for the other playbooks. During deployment, provide the Key Vault name when prompted and ensure the required secrets are present.
   - Create Microsoft Sentinel automation rules that invoke the relevant playbooks for matching incidents.

7. **Configure permissions:**

   - After deploying the playbooks, configure the required managed identity permissions.
   - Follow [Permissions.md](./Permissions.md) to grant the Logic Apps access to the Automation Account and Key Vault.

## Using Commvault Security Investigation Agent

1. Go to <https://securitycopilot.microsoft.com/agents>.
2. Search for “Commvault Security Investigation Agent”
3. Click on “Set up” Agent
4. Click on “Go to Agent”
5. Click **Run** -> **One time**.
6. Provide the **Hostname** and click **Submit**.

> **Note:** The hostname is the server whose Commvault and partner events you want to investigate. Availability of the agent and partner signals depends on the applicable Microsoft Security Copilot configuration and connected data sources.

## Automation Account and Runbooks Setup

### Why is an Automation Account Required?

The **Automation Account** is required for the included incident response playbooks. When Commvault security events trigger incidents in Microsoft Sentinel, the Logic App playbooks use automation runbooks to perform remediation actions through the Commvault APIs:

- **Commvault_Disable_IDP**: Automatically disables SAML identity providers when authentication compromise is detected
- **Commvault_Disable_User**: Automatically disables specific user accounts that show signs of compromise  
- **Commvault_Disable_Data_Aging**: Automatically disables data aging policies to prevent ransomware data loss

### Required Automation Account Name

The automation account **must** be named: `Commvault-Automation-Account`

This name is hardcoded in the Logic App playbooks and cannot be changed without modifying the playbook templates.

### Manual Runbook Deployment (Alternative Method)

If you prefer to set up the automation infrastructure manually instead of using the setup script:

1. **Create Automation Account:**
   - Azure Portal → Automation Accounts → Create
   - Name: `Commvault-Automation-Account`
   - Location: Same as your resource group

2. **Import Runbooks:**
   - Download the Python runbooks from the GitHub repository:
     - [Commvault_Disable_IDP.py](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_IDP.py)
     - [Commvault_Disable_User.py](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_User.py)
     - [Commvault_Disable_Data_Aging.py](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_Data_Aging.py)
   - Azure Portal → Automation Account → Runbooks → Import a runbook
   - Upload each Python file and publish the runbooks

### Automated Setup (Recommended)

For easier deployment, use the provided PowerShell script to create the Automation Account and publish the runbooks:

```powershell
./Setup-CommvaultAutomation.ps1
```

**What the script does:**
- Creates the `Commvault-Automation-Account` if it doesn't exist
- Downloads and publishes all three required runbooks automatically
- Validates the setup and provides status feedback

**To run the script:**
1. Open Azure Cloud Shell (PowerShell mode)
2. Upload the [Setup-CommvaultAutomation.ps1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Tools/Setup-CommvaultAutomation.ps1) script
3. Execute: `./Setup-CommvaultAutomation.ps1`
4. Follow the prompts to select your subscription and resource group

This script creates the Automation Account if it does not exist and publishes the three runbooks. It does not create the Key Vault, populate the required secrets, create the playbooks, or assign Logic App permissions; complete those steps separately using the instructions above and in [Permissions.md](./Permissions.md).

## Support

For support, contact Commvault at [support@commvault.com](mailto:support@commvault.com) or visit [Commvault Support](https://www.commvault.com/support).