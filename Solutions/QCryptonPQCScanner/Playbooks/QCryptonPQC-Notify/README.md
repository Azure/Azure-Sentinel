# QCryptonPQC-Notify

## Summary

This playbook is triggered when a Microsoft Sentinel incident is created by one of the QCrypton PQC Scanner analytic rules. It posts an Adaptive Card message to a Microsoft Teams channel summarising the quantum-vulnerable finding, including the incident title, severity, and a direct link to the incident in the Sentinel portal.

### Prerequisites

1. A Microsoft Teams team and channel where notifications should be posted.
2. The Teams Group ID and Channel ID for the target channel (retrieve these from Teams Admin Centre or the Graph API).
3. A user account with permissions to authorize the Microsoft Sentinel and Microsoft Teams API connections.

### Deployment Instructions

1. Click the **Deploy to Azure** button below to launch the ARM template deployment wizard.
2. Fill in the required parameters:
   - **PlaybookName**: Name of the Logic App (default: `QCryptonPQC-Notify`).
   - **TeamsGroupId**: The ID of the target Teams group (team).
   - **TeamsChannelId**: The ID of the target Teams channel.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQCryptonPQCScanner%2FPlaybooks%2FQCryptonPQC-Notify%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQCryptonPQCScanner%2FPlaybooks%2FQCryptonPQC-Notify%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each API connection:

1. Navigate to your Logic App in the Azure portal.
2. Go to **API connections** and select the **azuresentinel** connection resource.
3. Go to **General** > **Edit API connection**.
4. Click **Authorize**, sign in, and click **Save**.
5. Repeat the steps for the **teams** connection resource.

#### b. Assign Sentinel Responder role

The playbook's managed identity requires the **Microsoft Sentinel Responder** role on the Log Analytics workspace:

1. Go to **Log Analytics workspace** > **Access control (IAM)** > **Add role assignment**.
2. Select the **Microsoft Sentinel Responder** role.
3. Choose **Managed identity** and select the playbook's system-assigned identity.
4. Click **Save**.
