# QCryptonPQCEngine-Notify

## Summary

This playbook posts a notification to a Microsoft Teams channel when a Microsoft Sentinel incident is created from a QCrypton PQC Engine analytic rule (policy block, vulnerable algorithm, or PQC downgrade detection).

### Prerequisites

1. A Microsoft Teams team and channel where notifications should be posted.
2. The Teams Group ID and Channel ID for the target channel.

### Deployment instructions

1. Click the **Deploy to Azure** button below to launch the ARM template deployment wizard.
2. Fill in the required parameters:
   - **PlaybookName**: Name of the Logic App (default: `QCryptonPQCEngine-Notify`)
   - **TeamsGroupId**: The target Teams group (team) ID
   - **TeamsChannelId**: The target Teams channel ID

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQCryptonPQCEngine%2Fpqc-engine%2Fsentinel-solution%2FPlaybooks%2FQCryptonPQCEngine-Notify%2Fazuredeploy.json)

### Post-deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each API connection:

1. Navigate to the Logic App in the Azure Portal.
2. Click **API connections** in the left menu.
3. For each connection (Azure Sentinel, Teams):
   - Click the connection resource
   - Click **Edit API connection**
   - Click **Authorize**
   - Sign in and click **Save**

#### b. Configure automation in Microsoft Sentinel

1. In Microsoft Sentinel, go to **Automation**.
2. Create an automation rule that triggers this playbook when an incident is created from one of the PQC Engine analytic rules.
