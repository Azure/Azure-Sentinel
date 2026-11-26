# QCryptonPQCProxy-Notify

## Summary

This playbook is triggered when a Microsoft Sentinel incident is created by one of the QCrypton PQC Proxy analytic rules. It posts a message to a Microsoft Teams channel summarising the PQC Proxy alert, including the incident title, severity, and a direct link to the incident in the Sentinel portal.

### Prerequisites

1. A Microsoft Teams team and channel where notifications should be posted.
2. The Teams Group ID and Channel ID for the target channel (retrieve these from Teams Admin Centre or the Graph API).
3. A user account with permissions to authorize the Microsoft Teams API connection.

### Deployment Instructions

1. Click the **Deploy to Azure** button below to launch the ARM template deployment wizard.
2. Fill in the required parameters:
   - **PlaybookName**: Name of the Logic App (default: `QCryptonPQCProxy-Notify`).
   - **TeamsGroupId**: The ID of the target Teams group (team).
   - **TeamsChannelId**: The ID of the target Teams channel.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQCryptonPQCProxy%2FPlaybooks%2FQCryptonPQCProxy-Notify%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize the Teams connection

Once deployment is complete, authorize the Teams API connection:

1. Navigate to your Logic App in the Azure portal.
2. Go to **API connections** and select the **teams** connection resource.
3. Go to **General** > **Edit API connection**.
4. Click **Authorize**, sign in, and click **Save**.

The Sentinel connection uses the playbook's system-assigned managed identity and does not require manual authorization.

#### b. Assign Sentinel Responder role

The playbook's managed identity requires the **Microsoft Sentinel Responder** role on the Log Analytics workspace:

1. Go to **Log Analytics workspace** > **Access control (IAM)** > **Add role assignment**.
2. Select the **Microsoft Sentinel Responder** role.
3. Choose **Managed identity** and select the playbook's system-assigned identity.
4. Click **Save**.

#### c. Create an automation rule to run the playbook on incidents

The playbook will not run automatically until an automation rule attaches it to incident creation:

1. In Microsoft Sentinel, go to **Automation** > **Create** > **Automation rule**.
2. Set the trigger to **When incident is created**.
3. Under **Conditions**, add **Analytic rule name** contains `PQC` (or select the specific QCrypton PQC Proxy analytic rules).
4. Under **Actions**, select **Run playbook** and choose **QCryptonPQCProxy-Notify**.
5. Grant Microsoft Sentinel permissions to run the playbook by clicking **Manage playbook permissions** and selecting the resource group containing the playbook.
6. Click **Apply**.

### Troubleshooting

If incidents are created but no Teams notification appears, check the following:

1. **Automation rule not triggering** — In Microsoft Sentinel, go to **Automation** and verify the automation rule is enabled and its conditions match the analytic rules generating incidents. Check **Automation rule runs** for execution history.
2. **Playbook not invoked** — Open the Logic App in the Azure portal and go to **Overview** > **Runs history**. If no runs appear, the automation rule is not invoking the playbook. Verify that Sentinel has permission to run the playbook (**Manage playbook permissions** in the automation rule) and that the playbook is in the **Enabled** state.
3. **Playbook run fails at Sentinel trigger** — If runs appear but fail at the `Microsoft_Sentinel_incident` step, the managed identity may lack the **Microsoft Sentinel Responder** role. Re-check step (b) above.
4. **Playbook run fails at Teams action** — If the run fails at `Post_message_to_Teams`, the Teams API connection needs reauthorization. Go to **API connections** > the **teams** connection > **Edit API connection** > **Authorize** and sign in again. Ensure the authorizing account has permission to post to the target channel.
5. **Incorrect Team or Channel ID** — Verify the `TeamsGroupId` and `TeamsChannelId` parameter values match the target team and channel. Retrieve the correct IDs from Teams Admin Centre or via the Microsoft Graph API.
