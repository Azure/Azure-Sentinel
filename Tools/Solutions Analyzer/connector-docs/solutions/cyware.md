# Cyware

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cyware |
| **Support Tier** | Partner |
| **Categories** | domains |
| **First Published** | 2024-03-18 |
| **Last Updated** | 2024-03-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **3 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Hunting |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | Hunting |
| [`DeviceProcessEvents`](../tables/deviceprocessevents.md) | Hunting |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 3 |
| Playbooks | 2 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Detecting Suspicious PowerShell Command Executions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Hunting%20Queries/DetectingSuspiciousPowerShellCommandExecutions.yaml) | Execution | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Detecting Suspicious PowerShell Command Executions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Hunting%20Queries/UnusualNetworkConnectionsToRareExternalDomains.yaml) | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) |
| [Match Cyware Intel Watchlist Items With Common Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Hunting%20Queries/MatchCywareIntelWatchlistItemsWithCommonLogs.yaml) | CommandAndControl, Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Send Microsoft Sentinel Incident To Cyware Orchestrate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Playbooks/Send_Incident_To_Cyware_Orchestrate/azuredeploy.json) | Send Microsoft Sentinel Incident To Cyware Orchestrate | - |
| [azuredeploy.parameters](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Playbooks/Send_Incident_To_Cyware_Orchestrate/azuredeploy.parameters.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 06-03-2024                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
