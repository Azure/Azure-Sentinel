# Trend Micro Apex One

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-06 |
| **Last Updated** | 2022-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Trend Micro Apex One via Legacy Agent](../connectors/trendmicroapexone.md)
- [[Deprecated] Trend Micro Apex One via AMA](../connectors/trendmicroapexoneama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Trend Micro Apex One via AMA](../connectors/trendmicroapexoneama.md), [[Deprecated] Trend Micro Apex One via Legacy Agent](../connectors/trendmicroapexone.md) | Analytics, Hunting, Workbooks |

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
| [ApexOne - Attack Discovery Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneAttackDiscoveryDetectionRisks.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - C&C callback events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneRiskCnCEvents.yaml) | High | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Commands in Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneCommandsInRequest.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Device access permissions was changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneDvcAccessPermissionWasChanged.yaml) | Medium | PrivilegeEscalation | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Inbound remote access connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneInboundRemoteAccess.yaml) | High | LateralMovement | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Multiple deny or terminate actions on single IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneMultipleDenyOrTerminateActionOnSingleIp.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Possible exploit or execute operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOnePossibleExploitOrExecuteOperation.yaml) | High | PrivilegeEscalation, Persistence | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Spyware with failed response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneSpywareWithFailedResponse.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Suspicious commandline arguments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneCommandLineSuspiciousRequests.yaml) | High | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Suspicious connections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Analytic%20Rules/TMApexOneSuspiciousConnections.yaml) | High | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [ApexOne - Behavior monitoring actions by files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneBehaviorMonitoringTranslatedAction.yaml) | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Behavior monitoring event types by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneBehaviorMonitoringTypesOfEvent.yaml) | Privilege Escalation, Persistence | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Behavior monitoring operations by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneBehaviorMonitoringTranslatedOperation.yaml) | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Behavior monitoring triggered policy by command line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneBehaviorMonitoringTriggeredPolicy.yaml) | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Channel type by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneChannelType.yaml) | CommandandControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Data loss prevention action by IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneDataLossPreventionAction.yaml) | Collection | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Rare application protocols by Ip address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneRareAppProtocolByIP.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Spyware detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneSpywareDetection.yaml) | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Suspicious files events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneSuspiciousFiles.yaml) | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ApexOne - Top sources with alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Hunting%20Queries/TMApexOneTopSources.yaml) | Execution, InitialAccess, PrivilegeEscalation, DefenseEvasion, CommandAndControl, Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TrendMicroApexOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Workbooks/TrendMicroApexOne.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TMApexOneEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Parsers/TMApexOneEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 13-12-2024                     |  Removed Deprecated **Data  Connectors**                           |
| 3.0.2 	  | 12-07-2024 					   |  Deprecated **Data Connector** 									|
| 3.0.1       | 25-10-2023                     |  **Hunting Query** column corrected                                |   
| 3.0.0       | 22-09-2023                     |  Addition of new Trend Micro Apex One AMA **Data connector**       | 	                                                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
