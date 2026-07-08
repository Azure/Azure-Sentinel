Commvault Cloud - Microsoft Sentinel Integration
===============================================

This SOAR integration connects Commvault Cloud with Microsoft Sentinel to enable automated incident creation and response through Analytic Rules and Playbooks.

## Overview
This solution provides:
- **Data Ingestion**: Automated collection of Commvault client anomaly events via the Codeless Connector Framework
- **Incident Creation**: Automatic creation of Sentinel incidents based on Commvault anomaly detections
- **AI Powered Insights**: Use the Commvault Security Investigation Agent in Microsoft Security Copilot to correlate Commvault anomaly events with signals from tools like CrowdStrike, Netskope, and Palo Alto to validate impact on affected hosts and speed investigation.
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

The **Commvault Security IQ** data connector uses Microsoft's **Codeless Connector Framework (CCF)** — a fully managed, serverless poller hosted by Microsoft. No Azure Function App, Key Vault, or storage account is required. The solution package automatically deploys the required Data Collection Rule (DCR) and custom log table (`CommvaultAlertsCCF_CL`) into your workspace. A Data Collection Endpoint (DCE) must exist in your subscription; provide its resource ID as the `dceId` parameter during deployment.

Installation
------------

**1\. Create an API Token in Commvault:**

*   Follow the instructions in [Creating an Access Token](https://documentation.commvault.com/2024e/essential/creating_access_token.html).
*   Ensure the user creating the token has **Admin** or **Tenant Admin** privileges.
*   Copy the generated **QSDK Token** — you will need it in Step 4.

**2\. Install Commvault Cloud Solution:**

*   Sentinel -> [Your Workspace] -> Content hub -> Search "Commvault Cloud" -> Install.

**3\. Open the Data Connector:**

*   Sentinel -> Data connectors -> Search "Commvault Security IQ" -> Open connector page.

**4\. Configure the Connection:**

*   Under **Configuration**, enter the following:
    - **Commvault Environment Endpoint URL**: Your Commvault Cloud API base URL (e.g., `https://hostname/commandcenter/api`)
    - **QSDK Token**: The API token generated in Step 1
*   Click **Connect**.

The connector will begin polling the Commvault `/Client/Anomaly` API every 30 minutes and ingesting threat anomaly events into the `CommvaultAlertsCCF_CL` table in your Log Analytics workspace.

### Incident Detection and Response Setup Steps

**5\. Create Analytic Rules:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "Commvault Cloud Alert" -> Create Rule -> Next -> Save.

**6\. Create Playbooks:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> select a playbook -> Configuration -> Create Playbook -> Next -> Create.
*   Repeat for other playbooks.

**7\. Add Additional Permissions:**

*   After completing all the steps, ensure that the necessary additional permissions are configured.
*   Follow the instructions in [Permissions.md](./Permissions.md) to grant the required permissions for the Logic Apps.

## Using Commvault Security Investigation Agent

1. Go to https://securitycopilot.microsoft.com/agents
2. Search for “Commvault Security Investigation Agent”
3. Click on “Set up” Agent
4. Click on “Go to Agent”
5. Click on “Run” => “One time”
6. Provide “Hostname” and click “Submit”
> Note: Hostname is the name of the server that we want to check for events of Commvault and partners like Netskope, CrowdStrike and Palo Alto.

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