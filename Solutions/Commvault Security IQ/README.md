Commvault Cloud - Microsoft Sentinel Integration
===============================================

This SOAR integration connects Commvault Cloud with Microsoft Sentinel to enable automated incident creation and response through Analytic Rules and Playbooks.

## Overview
This solution provides:
- **Data Ingestion**: Automated collection of Commvault security alerts and anomalies
- **Incident Creation**: Automatic creation of Sentinel incidents based on Commvault security events
- **Incident Response**: Playbooks for automated remediation actions (disable users, disable data aging, etc.)

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

## Required Azure Resources
The following Azure resources will be created or configured during this installation:

### Key Vault
- **Purpose**: Securely stores Commvault credentials and API endpoints
- **Required Secrets**:
  - `access-token`: Your Commvault Cloud access token
  - `environment-endpoint-url`: Your Commvault Cloud API endpoint URL (Commvault/Metallic endpoint URL : https://`hostname`/commandcenter/api )
  - `refresh-token`: Your Commvault Cloud refresh token
  - `token-expiry-timestamp`: Auto-managed (by data connector) token expiration tracking

Installation
------------

**1\. Create Access Token in Commvault:**

*   Follow the instructions in [Creating an Access Token / Refresh Token](https://documentation.commvault.com/2024e/essential/creating_access_token.html).
*   Ensure the user creating the token has **Admin** or **Tenant Admin** privileges.

**2\. Create KeyVault:**

*   Azure Portal -> KeyVault -> Create -> Basics (select subscription, RG).

**3\. Create KeyVault Secrets:**

*   Azure Portal -> KeyVault -> Secrets -> Generate/Import -> Manual:
    *   Name: access-token, Value: (Your Commvault/Metallic access token), Enabled: Yes -> Create.
    *   Name: refresh-token, Value: (Your Commvault/Metallic refresh token), Enabled: Yes -> Create.
    *   Name: environment-endpoint-url, Value: (Your Commvault/Metallic endpoint's URL), Enabled: Yes -> Create.

**4\. Install Commvault Cloud Solution:**

*   Sentinel -> Content hub -> Search "Commvault Cloud" -> Install.

**5\. Configure Data Connector:**

*   Commvault Cloud -> CommvaultSecurityIQ (using Azure Functions) -> Open connector page -> Deploy to Azure -> Fill details -> Create.
*   For a detailed step-by-step guide, refer to [DataConnector.md](./DataConnector.md).

**6\. Upload and Run Setup Script:**

**Why run the Setup Script?**

The setup script automates the creation of Azure resources needed for automated incident response. It will:

*   Create an Automation Account (named Commvault-Automation-Account) and deploys runbooks for remediation actions (disable user, disable data aging, etc.)
*   Generate refresh tokens in your Key Vault (if they don't already exist)
*   Validate that all required secrets are properly configured

> **Note:** You must have sufficient permissions to view and edit secrets in the Azure Key Vault before running the setup script. Without these permissions, the script will fail to update existing secrets as required.

*   Open **Azure Cloud Shell** in PowerShell mode:
    1. Navigate to the **Azure Portal**.
    2. Click on the **Cloud Shell** icon in the top-right corner of the portal.
    3. If prompted, select **PowerShell** as the shell environment (instead of Bash).
    4. If this is your first time using Cloud Shell, you may need to create a storage account to persist your files. Follow the on-screen instructions to set it up.

*   Manage files -> [Setup-CommvaultAutomation.ps1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Tools/Setup-CommvaultAutomation.ps1) -> Run: `./Setup-CommvaultAutomation.ps1`

**7\. Create Analytic Rules:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "Commvault Cloud Alert" -> Create Rule -> Next -> Save.

**8\. Create Playbooks:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "logic-app-disable-data-aging" -> Configuration -> "Commvault Disable Data Aging Logic App Playbook" -> Create Playbook -> Next -> Enter keyvaultName -> Create Playbook.
*   Repeat for other playbooks.

**9\. Add Additional Permissions:**

*   After completing all the steps, ensure that the necessary additional permissions are configured.
*   Follow the instructions in [Permissions.md](./Permissions.md) to grant the required permissions for the Logic Apps.
*   Additionally, refer to **6. Post-Deployment Steps** in [DataConnector.md](./DataConnector.md) to ensure the Function App has the necessary permissions to access the Key Vault.
