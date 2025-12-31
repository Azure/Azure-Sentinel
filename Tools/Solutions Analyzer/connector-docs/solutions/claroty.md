# Claroty

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Claroty via Legacy Agent](../connectors/claroty.md)
- [[Deprecated] Claroty via AMA](../connectors/clarotyama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Claroty via AMA](../connectors/clarotyama.md), [[Deprecated] Claroty via Legacy Agent](../connectors/claroty.md) | Analytics, Hunting, Workbooks |

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
| [Claroty - Asset Down](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyAssetDown.yaml) | High | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Critical baseline deviation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyCriticalBaselineDeviation.yaml) | High | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Login to uncommon location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyLoginToUncommonSite.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Multiple failed logins by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyMultipleFailedLogin.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Multiple failed logins to same destinations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyMultipleFailedLoginsSameDst.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - New Asset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyNewAsset.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Policy violation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyPolicyViolation.yaml) | High | Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Suspicious activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotySuspiciousActivity.yaml) | High | Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Suspicious file transfer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotySuspiciousFileTransfer.yaml) | High | Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Treat detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Analytic%20Rules/ClarotyTreat.yaml) | High | Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Claroty - Baseline deviation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyBaselineDeviation.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Conflict assets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyConflictAssets.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Critical Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyCriticalEvents.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Network scan sources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyScanSources.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Network scan targets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyScantargets.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - PLC logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyPLCLogins.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Unapproved access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyUnapprovedAccess.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Unresolved alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyUnresolvedAlerts.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - User failed logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotySRAFailedLogins.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Claroty - Write and Execute operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Hunting%20Queries/ClarotyWriteExecuteOperations.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ClarotyOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Workbooks/ClarotyOverview.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ClarotyEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Parsers/ClarotyEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.3       | 18-11-2024                     | Removed Deprecated **Data Connectors**         |  
| 3.0.2 	  | 10-07-2024 					   | Deprecated **Data Connector** 					|
| 3.0.1       | 11-09-2023                     | Addition of new Claroty AMA **Data Connector** |
| 3.0.0       | 27-07-2023                     | Corrected the links in the solution.           |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
