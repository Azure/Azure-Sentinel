# Microsoft Windows SQL Server Database Audit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-11-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`SQLEvent`](../tables/sqlevent.md) | Hunting |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 9 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Failed Logon Attempts on SQL Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-Failed%20SQL%20Logons.yaml) | CredentialAccess | [`SQLEvent`](../tables/sqlevent.md) |
| [Failed Logon on SQL Server from Same IPAddress in Short time Span](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-MultipleFailedLogon_FromSameIP.yaml) | CredentialAccess | [`SQLEvent`](../tables/sqlevent.md) |
| [Multiple Failed Logon on SQL Server in Short time Span](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-MultipleFailedLogon_InShortSpan.yaml) | CredentialAccess | [`SQLEvent`](../tables/sqlevent.md) |
| [New User created on SQL Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-New_UserCreated.yaml) | Persistence | [`SQLEvent`](../tables/sqlevent.md) |
| [SQL User deleted from Database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-UserDeletedFromDatabase.yaml) | Persistence, PrivilegeEscalation, Impact | [`SQLEvent`](../tables/sqlevent.md) |
| [User Role altered on SQL Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-UserRoleChanged.yaml) | Persistence, PrivilegeEscalation | [`SQLEvent`](../tables/sqlevent.md) |
| [User added to SQL Server SecurityAdmin Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-UserAdded_to_SecurityAdmin.yaml) | Persistence, PrivilegeEscalation | [`SQLEvent`](../tables/sqlevent.md) |
| [User removed from SQL Server Roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-UserRemovedFromServerRole.yaml) | Persistence, PrivilegeEscalation, Impact | [`SQLEvent`](../tables/sqlevent.md) |
| [User removed from SQL Server SecurityAdmin Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Windows%20SQL%20Server%20Database%20Audit/Hunting%20Queries/SQL-UserRemovedFromSecurityAdmin.yaml) | Persistence, PrivilegeEscalation, Impact | [`SQLEvent`](../tables/sqlevent.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 18-03-2024                     | Change in **Hunting Queries** description   | 
| 3.0.0       | 10-07-2023                     | Updated **Parser** to correctly parse failed login events | 
|             |                                | Added Entity mapping and version in all the **Hunting Queries** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
