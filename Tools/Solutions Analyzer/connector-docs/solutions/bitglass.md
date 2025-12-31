# Bitglass

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Bitglass](../connectors/bitglass.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) | [Bitglass](../connectors/bitglass.md) | Analytics, Hunting, Workbooks |

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
| [Bitglass - Impossible travel distance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassImpossibleTravelDistance.yaml) | Medium | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Login from new device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassNewDevice.yaml) | Medium | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Multiple failed logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassMultipleFailedLogins.yaml) | High | CredentialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Multiple files shared with external entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassFilesSharedWithExternal.yaml) | Medium | Exfiltration | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - New admin user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassNewAdminUser.yaml) | Medium | PrivilegeEscalation | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - New risky user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassNewRiskyUser.yaml) | High | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Suspicious file uploads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassSuspiciousFileUpload.yaml) | High | Exfiltration | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - The SmartEdge endpoint agent was uninstalled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassSmartEdgeAgentUninstall.yaml) | Medium | DefenseEvasion | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - User Agent string has changed for user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassUserUAChanged.yaml) | Medium | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - User login from new geo location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Analytic%20Rules/BitglassUserLoginNewGeoLocation.yaml) | Medium | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Bitglass - Applications used](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassApplications.yaml) | Exfiltration | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Insecure web protocol](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassInsecureWebProtocol.yaml) | Exfiltration | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Login failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassLoginFailures.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - New applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassNewApplications.yaml) | Exfiltration | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassNewUsers.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Privileged login failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassPrivilegedLoginFailures.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Risky users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassRiskyUsers.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Risky users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassTopUsersWithBlocks.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - Uncategorized resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassUncategorizedResources.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |
| [Bitglass - User devices](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Hunting%20Queries/BitglassUserDevices.yaml) | InitialAccess | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Bitglass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Workbooks/Bitglass.json) | [`BitglassLogs_CL`](../tables/bitglasslogs-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Bitglass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Parsers/Bitglass.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 21-10-2024                     | Updated the python runtime version to **3.11** and updated functional URL|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
