# NordPass Integration with Microsoft Sentinel

## Overview
This solution lets you monitor your organization’s user activities and track security incidents from NordPass’ Activity Log.

The benefits of this integration:
- **Enhanced Security Monitoring:** Detect unauthorized access and security risks.
- **Automated Threat Detection:** Receive real-time alerts on suspicious activities.
- **Centralized Activity Logging:** Maintain a comprehensive audit trail of user activities.

## Resources Created
Once you deploy the solution, the following Azure resources will be created:

<details>
<summary><strong>Azure Function</strong></summary>
An <strong>Azure Function</strong> is a serverless solution that synchronizes activity between NordPass and Microsoft Sentinel.
</details>

<details>
<summary><strong>Storage Account</strong></summary>
A <strong>Storage Account</strong> contains Azure Function settings and configurations.
</details>

<details>
<summary><strong>Custom Table</strong></summary>
A <strong>Log Analytics Table</strong> named <code>NordPassEventLogs_CL</code> will be created to store synchronized activity events from NordPass. This table serves as the central repository for all collected log data.
</details>

<details>
<summary><strong>Workbook</strong></summary>
A <strong>Workbook</strong> will be created to aggregate NordPass activity data for enhanced visualization and analysis. Dashboards in this workbook give insights into your user’s activity trends, security alerts, and compliance statuses.
</details>

<details>
<summary><strong>Analytic Rules</strong></summary>
Multiple <strong>Analytic Rules</strong> will be created to facilitate incident escalation, allowing security teams to respond to threats proactively. 

These rules include:
- Users declining invites
- Bulk deletion of items
- Deleted users items were reassigned
- Invites, suspensions, and deletions by Owners or Admins
- Revoking tokens
- Failed login attempts by users
- Users exporting their vault

These rules help automate security monitoring, creating actionable insights for your organization.
</details>

## Requirements
To deploy this integration, ensure you have the following:
- [NordPass Enterprise plan](https://nordpass.com/plans/business/).
- [Token for Microsoft Sentinel integration](https://support.nordpass.com/hc/en-us/articles/31972037289873)
- [Microsoft Azure](https://azure.microsoft.com/free).
- [Microsoft Sentinel](https://azure.microsoft.com/products/microsoft-sentinel/)

You must also be a Contributor with User Access Administrator role or Owner of the Microsoft Sentinel Resource Group. This is needed to assign the correct RBAC role to Function App’s managed identity

## Installation
You can easily install the NordPass Solution for Microsoft Sentinel in a few minutes. Click the button below to start the deployment wizard:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-Nordpass-azuredeploy)

## Post-Deployment Configuration
Once you’ve deployed the solution, follow these steps to finalize the integration:
1. **Verify Data Ingestion:** Check that NordPass logs appear in the `NordPassEventLogs_CL` table in Microsoft Sentinel.
2. **Configure Analytic Rules:** Adjust thresholds and settings for alerts based on your security needs.
3. **Set Up Dashboard Views:** Use the workbook to create visual reports and enhance monitoring efficiency.
4. **Test Incident Response:** Trigger test events to ensure the analytic rules are working as expected.

## Support & Troubleshooting
If you encounter issues during deployment or need assistance, please use the resources below:
- **NordPass Support:** [Contact Support](https://support.nordpass.com/hc/en-us/requests/new)
- **Microsoft Azure Documentation:** [Azure Sentinel Documentation](https://docs.microsoft.com/azure/sentinel/)
