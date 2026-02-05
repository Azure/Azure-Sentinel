Commvault Cloud - Microsoft Sentinel Integration
===============================================

This SOAR integration connects Commvault Cloud with Microsoft Sentinel to enable automated incident creation and response through Analytic Rules and Playbooks.

## Overview
This solution provides:
- **Data Ingestion**: Automated collection of Commvault security events and anomalies
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

### Configurable Environment Variables ( Optional )

The following environment variables can be optionally configured to customize the Function App behavior:

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `NumberOfDaysToBackfill` | 7 | Number of days to backfill data on initial run |
| `ShowAllEvents` | false | Include all events (true/false) |
| `AZURE_CLIENT_ID` | - | Managed Identity Client ID (uses DefaultAzureCredential if not set) |

**Configuration Notes:**
- These variables are optional - the Function App will work with default values if not specified
- **By default, only security-relevant events are collected**: The data connector filters for Commvault events related to anomalies and malware/ransomware threats as documented in the [Threat Indicators Dashboard](https://documentation.commvault.com/2024e/commcell-console/threat_indicators_dashboard.html) . Use `ShowAllEvents` to disable filtering of events. It is recommended to have data retention policy, when allowing all events , so the log analytics workspace is not bloated with events.
- Event level filters control which Commvault events are collected based on severity
- `NumberOfDaysToBackfill` determines how far back to collect events on the first run only
- `AZURE_CLIENT_ID` is only needed if using a specific Managed Identity instead of the default

### Incident Detection and Response Setup Steps

**6\. Create Analytic Rules:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "Commvault Cloud Alert" -> Create Rule -> Next -> Save.

**7\. Create Playbooks:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "logic-app-disable-data-aging" -> Configuration -> "Commvault Disable Data Aging Logic App Playbook" -> Create Playbook -> Next -> Enter keyvaultName -> Create Playbook.
*   Repeat for other playbooks.

**8\. Add Additional Permissions:**

*   After completing all the steps, ensure that the necessary additional permissions are configured.
*   Follow the instructions in [Permissions.md](./Permissions.md) to grant the required permissions for the Logic Apps.
*   Additionally, refer to **6. Post-Deployment Steps** in [DataConnector.md](./DataConnector.md) to ensure the Function App has the necessary permissions to access the Key Vault.

## Automation Account and Runbooks Setup

### Why is an Automation Account Required?

The **Automation Account** is essential for automated incident response in this solution. When Commvault security events trigger incidents in Microsoft Sentinel, the Logic App playbooks use automation runbooks to perform immediate remediation actions via Commvault APIs:

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

For easier deployment, use the provided PowerShell script that automates the entire automation account and runbook setup:

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

This script eliminates manual steps and ensures consistent deployment of the automation infrastructure required for incident response.