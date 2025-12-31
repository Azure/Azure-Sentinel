# OracleDatabaseAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Oracle Database Audit](../connectors/oracledatabaseaudit.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Oracle Database Audit](../connectors/oracledatabaseaudit.md) | Analytics, Hunting, Workbooks |

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
| [OracleDBAudit - Connection to database from external IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditConnectFromExternalIp.yaml) | Medium | InitialAccess, Collection, Exfiltration | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Connection to database from unknown IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditForbiddenSrcIpAddr.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Multiple tables dropped in short time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditDropManyTables.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - New user account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditNewUserDetected.yaml) | Low | InitialAccess, Persistence | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Query on Sensitive Table](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditQueryOnSensitiveTable.yaml) | Medium | Collection | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - SQL injection patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditSQLInjectionPatterns.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Shutdown Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditShutdownServer.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Unusual user activity on multiple tables](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditSelectOnManyTables.yaml) | Medium | Collection | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - User activity after long inactivity time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditRareUserActivity.yaml) | Medium | InitialAccess, Persistence | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - User connected to database from new IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Analytic%20Rules/OracleDBAuditNewIpForUser.yaml) | Low | InitialAccess | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [OracleDBAudit - Action by Ip](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditActionsByIp.yaml) | InitialAccess, DefenseEvasion, Collection, Impact | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Action by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditActionsByUser.yaml) | InitialAccess, DefenseEvasion, Collection, Impact | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Active Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditActiveUsers.yaml) | InitialAccess, DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Audit large queries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditLargeQueries.yaml) | InitialAccess, DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Dropped Tables](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditDroppedTables.yaml) | Impact | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Inactive Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditInactiveUsers.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Top tables queries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditListOfTablesQueried.yaml) | Collection | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Users Privileges Review](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditUsersPrivilegesReview.yaml) | InitialAccess, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Users connected to databases during non-operational hours.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditDbConnectNonOperationalTime.yaml) | InitialAccess, DefenseEvasion, Collection, Impact | [`Syslog`](../tables/syslog.md) |
| [OracleDBAudit - Users with new privileges](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Hunting%20Queries/OracleDBAuditUsersNewPrivilegesAdded.yaml) | InitialAccess, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [OracleDatabaseAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Workbooks/OracleDatabaseAudit.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OracleDatabaseAuditEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Parsers/OracleDatabaseAuditEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 11-12-2024                     | Removed Deprecated Data connectors          |
| 3.0.2       | 23-07-2024                     | Deprecated data connectors                  |
| 3.0.1       | 26-04-2024                     | Repackaged for fix on parser in maintemplate to have old parsername and parentid                    |
| 3.0.0       | 19-12-2023                     | Documentation changes for oracle data base audit  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
