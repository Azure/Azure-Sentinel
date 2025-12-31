# Box

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Box](../connectors/boxdataconnector.md)
- [Box Events (CCP)](../connectors/boxeventsccpdefinition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BoxEventsV2_CL`](../tables/boxeventsv2-cl.md) | [Box Events (CCP)](../connectors/boxeventsccpdefinition.md) | - |
| [`BoxEvents_CL`](../tables/boxevents-cl.md) | [Box](../connectors/boxdataconnector.md), [Box Events (CCP)](../connectors/boxeventsccpdefinition.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Box - Abmormal user activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxAbnormalUserActivity.yaml) | Medium | Collection | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Executable file in folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxBinaryFile.yaml) | Medium | InitialAccess | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - File containing sensitive data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxSensitiveFile.yaml) | Medium | Exfiltration | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Forbidden file type downloaded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxDownloadForbiddenFiles.yaml) | Medium | InitialAccess | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Inactive user login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxInactiveUserLogin.yaml) | Medium | InitialAccess | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Item shared to external entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxItemSharedToExternalUser.yaml) | Medium | Exfiltration | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Many items deleted by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxMultipleItemsDeletedByUser.yaml) | Medium | Impact | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - New external user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxNewExternalUser.yaml) | Medium | InitialAccess, Persistence | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - User logged in as admin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxUserLoginAsAdmin.yaml) | Medium | PrivilegeEscalation | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - User role changed to owner](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Analytic%20Rules/BoxUserRoleChangedToOwner.yaml) | Medium | PrivilegeEscalation | [`BoxEvents_CL`](../tables/boxevents-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Box - Deleted users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxDeletedUsers.yaml) | Impact | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Downloaded data volume per user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxUserDownloadsByVolume.yaml) | Exfiltration, Collection | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - IP list for admin users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxAdminIpAddress.yaml) | InitialAccess, PrivilegeEscalation | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Inactive admin users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxInactiveAdmins.yaml) | PrivilegeEscalation | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Inactive users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxInactiveUsers.yaml) | InitialAccess | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxNewUsers.yaml) | PrivilegeEscalation, Persistence | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxUserGroupChanges.yaml) | PrivilegeEscalation | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Suspicious or sensitive files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxSuspiciousFiles.yaml) | Exfiltration | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Uploaded data volume per user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxUserUploadsByVolume.yaml) | Exfiltration, Collection | [`BoxEvents_CL`](../tables/boxevents-cl.md) |
| [Box - Users with owner permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Hunting%20Queries/BoxUsersWithOwnerPermissions.yaml) | PrivilegeEscalation | [`BoxEvents_CL`](../tables/boxevents-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Box](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Workbooks/Box.json) | [`BoxEvents_CL`](../tables/boxevents-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [BoxEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Parsers/BoxEvents.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.2       | 29-10-2025                     | Updated KQL queries in Workbook to use EventEndTime instead of TimeGenerated for time-based filtering |
| 3.1.1       | 10-02-2025                     | Advancing CCP **Data Connector** from Public preview to Global Availability.|
| 3.1.0       | 06-12-2024                     | Added new CCP **Data Connector** and modified **Parser**.           |
| 3.0.1       | 18-08-2023                     | Added text 'using Azure Functions' in **Data Connector** page.      |
| 3.0.0       | 19-07-2023                     | Manual deployment instructions updated for **Data Connector**.		|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
