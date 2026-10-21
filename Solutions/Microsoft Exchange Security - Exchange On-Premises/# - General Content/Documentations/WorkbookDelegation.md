# Delegate access to Microsoft Exchange Security workbooks

## Overview

Use Microsoft Entra groups and Azure role-based access control (RBAC) to delegate workbook access. Assign roles to groups instead of individual users whenever possible.

Workbook access has two independent parts:

1. Permission to open the Azure workbook resource.
2. Permission to query every Log Analytics table used by that workbook.

Granting access to the workbook does not grant access to its data, and granting access to Log Analytics data does not grant access to the workbook resource.

## Recommended access model

| Scope | Recommended role | Purpose |
|-------|------------------|---------|
| Resource group containing the saved workbooks | **Workbook Reader** | Open and use saved workbooks |
| Resource group containing the saved workbooks | **Workbook Contributor** | Optional: edit and save workbooks |
| Log Analytics workspace | **Log Analytics Data Reader** with granular RBAC conditions | Query only the tables required by the workbooks |

For current Microsoft guidance, see:

- [Use workbooks in Microsoft Sentinel](https://learn.microsoft.com/azure/sentinel/monitor-your-data)
- [Manage table-level access in a Log Analytics workspace](https://learn.microsoft.com/azure/azure-monitor/logs/manage-table-access)
- [Configure granular RBAC for Log Analytics](https://learn.microsoft.com/azure/azure-monitor/logs/granular-rbac-log-analytics)

The older dual-role method based on a custom workspace role and table-scoped **Reader** assignments is retained by Azure Monitor for compatibility, but granular RBAC is the recommended approach for new deployments.

## Identify the required tables

Grant access only to tables queried by the workbooks that the group will use. The standard workbooks can require:

| Solution | Current configuration table | Additional tables |
|----------|-----------------------------|-------------------|
| Exchange On-Premises | `ESIAPIExchangeOnPremConfig_CL` | `Event` for administrative audit activity; `ESIExchangeConfig_CL` when historical data from the legacy ingestion API is required |
| Exchange Online | `ESIAPIExchangeOnlineConfig_CL` | `OfficeActivity` for administrative activity; `ESIExchangeOnlineConfig_CL` when historical data from the legacy ingestion API is required |

Customized workbooks can query other tables. Review each workbook query before finalizing the role condition.

## Configure delegation

### 1. Create the Microsoft Entra group

1. Create a security group, for example `ESI-Workbook-Readers`.
2. Add the users who require access.
3. If workbook editors require broader permissions than readers, create a separate editor group.

### 2. Save the workbooks

Save the required templates as Azure workbook resources by following [Deploy Microsoft Exchange Security workbooks](./WorkbookDeployement.md).

You can store the saved workbooks in a dedicated resource group to simplify role assignments. A saved workbook is independent of its solution template and is not updated automatically when the solution changes.

### 3. Grant access to the workbook resources

1. Open the resource group that contains the saved workbooks.
2. Open **Access control (IAM)**.
3. Add a role assignment.
4. Assign **Workbook Reader** to the reader group.
5. If required, assign **Workbook Contributor** to the editor group.

Avoid assigning the general **Reader** or **Contributor** role when the workbook-specific roles provide sufficient access.

### 4. Grant access to workbook data

1. Open the Log Analytics workspace used by Microsoft Sentinel.
2. Follow the Microsoft procedure to create a granular RBAC assignment.
3. Use the built-in **Log Analytics Data Reader** role.
4. Add a condition that permits access only to the tables required by the selected workbooks.
5. Assign the conditioned role to the Microsoft Entra reader group.

Do not also assign a broader workspace role that grants access to all log data, because that would bypass the intended table restriction.

### 5. Validate the delegated access

Use a test account that is a member of the delegated group and verify that it can:

1. Open each saved workbook.
2. Run every workbook query without authorization errors.
3. Query only the intended Log Analytics tables.
4. Save changes only if it belongs to the editor group.

After validation, share the saved workbook URL or the dedicated resource group with the authorized users.

## Maintenance

- Review group membership regularly.
- Update granular RBAC conditions when workbook queries or ingestion tables change.
- Revalidate access after solution upgrades.
- Compare customized saved workbooks with updated templates before manually applying template improvements.
