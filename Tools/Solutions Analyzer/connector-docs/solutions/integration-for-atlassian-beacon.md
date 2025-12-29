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

This solution provides **1 data connector(s)**.

### [Atlassian Beacon Alerts](../connectors/atlassianbeaconalerts.md)

**Publisher:** DEFEND Ltd.

Atlassian Beacon is a cloud product that is built for Intelligent threat detection across the Atlassian platforms (Jira, Confluence, and Atlassian Admin). This can help users detect, investigate and respond to risky user activity for the Atlassian suite of products. The solution is  a custom data connector from DEFEND Ltd. that is used to visualize the alerts ingested from Atlassian Beacon to Microsoft Sentinel via a Logic App.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `atlassian_beacon_alerts_CL` |
| **Connector Definition Files** | [AtlassianBeacon_DataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Integration%20for%20Atlassian%20Beacon/Data%20Connectors/AtlassianBeacon_DataConnector.json) |

[→ View full connector details](../connectors/atlassianbeaconalerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `atlassian_beacon_alerts_CL` | [Atlassian Beacon Alerts](../connectors/atlassianbeaconalerts.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.3       | 04-03-2024                     | Updated title to comply with Atlassian                                   |
| 3.0.2       | 23-01-2024                     | Replaced Atlassian Beacon Logo with Official Azure Sentinel Logo         |
| 3.0.1       | 04-12-2023                     | Atlassian Beacon Payload update in Integration                           |
| 3.0.0       | 24-10-2023                     | Initial Solution Release                                                 |

[← Back to Solutions Index](../solutions-index.md)
