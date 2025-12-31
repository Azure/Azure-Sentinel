# Integration for Atlassian Beacon

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | DEFEND Ltd. |
| **Support Tier** | Partner |
| **Support Link** | [https://www.defend.co.nz/](https://www.defend.co.nz/) |
| **Categories** | domains |
| **First Published** | 2023-09-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Integration%20for%20Atlassian%20Beacon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Integration%20for%20Atlassian%20Beacon) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Atlassian Beacon Alerts](../connectors/atlassianbeaconalerts.md)

## Tables Reference

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`atlassian_beacon_alerts_CL`](../tables/atlassian-beacon-alerts-cl.md) | [Atlassian Beacon Alerts](../connectors/atlassianbeaconalerts.md) | Analytics, Playbooks (writes) |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Atlassian Beacon Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Integration%20for%20Atlassian%20Beacon/Analytic%20Rules/AtlassianBeacon_High.yaml) | High | - | *Internal use:*<br>[`atlassian_beacon_alerts_CL`](../tables/atlassian-beacon-alerts-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Atlassian Beacon Integration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Integration%20for%20Atlassian%20Beacon/Playbooks/Sync%20Alerts/azuredeploy.json) | This Logic App recieves a webhook from Atlassian Beacon and ingest the payload into Microsoft Sentin... | *Internal use:*<br>[`atlassian_beacon_alerts_CL`](../tables/atlassian-beacon-alerts-cl.md) *(write)* |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.3       | 04-03-2024                     | Updated title to comply with Atlassian                                   |
| 3.0.2       | 23-01-2024                     | Replaced Atlassian Beacon Logo with Official Azure Sentinel Logo         |
| 3.0.1       | 04-12-2023                     | Atlassian Beacon Payload update in Integration                           |
| 3.0.0       | 24-10-2023                     | Initial Solution Release                                                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
