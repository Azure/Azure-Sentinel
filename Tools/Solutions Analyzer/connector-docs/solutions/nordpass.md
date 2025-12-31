# NordPass

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | NordPass |
| **Support Tier** | Partner |
| **Support Link** | [https://support.nordpass.com/](https://support.nordpass.com/) |
| **Categories** | domains |
| **First Published** | 2025-04-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [NordPass](../connectors/nordpass.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) | [NordPass](../connectors/nordpass.md) | Analytics, Workbooks |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 9 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [NordPass - Activity token revocation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_token_revoked.yaml) | Medium | DefenseEvasion | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - Declined invitation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_Invite_declined.yaml) | Low | DefenseEvasion | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - Deleting items of deleted member](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_items_reassignment_deletion.yaml) | High | Impact | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - Domain data detected in breach](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_domain_data_detected_in_breach.yaml) | High | Exfiltration | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - Manual invitation, suspension, or deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_manual_user_manipulation.yaml) | Medium | Persistence | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - User data detected in breach](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_user_data_detected_in_breach.yaml) | High | Exfiltration | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - User deletes items in bulk](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_items_bulk_delete.yaml) | High | Impact, Collection | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - User fails authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_user_login_failed.yaml) | High | CredentialAccess | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |
| [NordPass - Vault export](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Analytic%20Rules/nordpass_vault_exported.yaml) | High | Exfiltration | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NordPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Workbooks/NordPass.json) | [`NordPassEventLogs_CL`](../tables/nordpasseventlogs-cl.md) |

## Additional Documentation

> 📄 *Source: [NordPass/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/README.md)*

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

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**        |
|-------------|--------------------------------|---------------------------|
| 3.0.1       | 25-08-2025                     | Added new Activity Logs   |
| 3.0.0       | 22-04-2025                     | Initial Solution Release. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
