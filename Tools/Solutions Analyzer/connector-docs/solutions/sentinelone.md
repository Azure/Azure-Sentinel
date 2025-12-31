# SentinelOne

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-11-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [SentinelOne](../connectors/sentinelone.md)
- [SentinelOne](../connectors/sentineloneccp.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SentinelOneActivities_CL`](../tables/sentineloneactivities-cl.md) | [SentinelOne](../connectors/sentineloneccp.md) | - |
| [`SentinelOneAgents_CL`](../tables/sentineloneagents-cl.md) | [SentinelOne](../connectors/sentineloneccp.md) | - |
| [`SentinelOneAlerts_CL`](../tables/sentinelonealerts-cl.md) | [SentinelOne](../connectors/sentineloneccp.md) | - |
| [`SentinelOneGroups_CL`](../tables/sentinelonegroups-cl.md) | [SentinelOne](../connectors/sentineloneccp.md) | - |
| [`SentinelOneThreats_CL`](../tables/sentinelonethreats-cl.md) | [SentinelOne](../connectors/sentineloneccp.md) | - |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | [SentinelOne](../connectors/sentinelone.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Sentinel One - Admin login from new location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneAdminLoginNewIP.yaml) | High | InitialAccess, PrivilegeEscalation | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Agent uninstalled from multiple hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneAgentUninstalled.yaml) | High | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Alert from custom rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneAlertFromCustomRule.yaml) | High | InitialAccess | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Blacklist hash deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneBlacklistHashDeleted.yaml) | Medium | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Exclusion added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneExclusionAdded.yaml) | Medium | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Multiple alerts on host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneMultipleAlertsOnHost.yaml) | High | InitialAccess | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - New admin created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneNewAdmin.yaml) | Medium | PrivilegeEscalation | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Rule deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneRuleDeleted.yaml) | Medium | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Rule disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneRuleDisabled.yaml) | Medium | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Same custom rule triggered on different hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneSameCustomRuleHitOnDiffHosts.yaml) | High | InitialAccess, LateralMovement | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - User viewed agent's passphrase](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Analytic%20Rules/SentinelOneViewAgentPassphrase.yaml) | Medium | CredentialAccess | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Sentinel One - Agent not updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneAgentNotUpdated.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Agent status](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneAgentStatus.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Alert triggers (files, processes, strings)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneAlertTriggers.yaml) | InitialAccess | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Deleted rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneRulesDeleted.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Hosts not scanned recently](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneHostNotScanned.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - New rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneNewRules.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Scanned hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneScannedHosts.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Sources by alert count](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneSourcesByAlertCount.yaml) | InitialAccess | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Uninstalled agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneUninstalledAgents.yaml) | DefenseEvasion | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |
| [Sentinel One - Users by alert count](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Hunting%20Queries/SentinelOneUsersByAlertCount.yaml) | InitialAccess | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SentinelOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Workbooks/SentinelOne.json) | [`SentinelOne_CL`](../tables/sentinelone-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SentinelOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Parsers/SentinelOne.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.6       | 10-02-2025                     | Advancing CCP **Data Connector** from Public preview to Global Availability.|
| 3.0.5       | 20-01-2025                     | Updated "Sentinel One - Agent uninstalled from multiple hosts" **Analytic Rule** with  ActivityType  |
| 3.0.4       | 15-01-2025                     | Added older Function app **Data Connector** again to SOlution until final deprecation of Function app happens  |
| 3.0.3       | 12-12-2024                     | Added new CCP **Data Connector** and Updated **Parser**  |
| 3.0.2       | 11-09-2024                     | Updated the python runtime version to 3.11 in **Data Connector** Function App  |
| 3.0.1       | 03-05-2024                     | Repackaged for **Parser** issue fix             |
| 3.0.0       | 28-07-2023                     | Bug fixes in API version.                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
