# Cisco Meraki Events via REST API

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Meraki%20Events%20via%20REST%20API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Meraki%20Events%20via%20REST%20API) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimAuditEventLogs`](../tables/asimauditeventlogs.md) | [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md) | - |
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md) | - |
| [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) | [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 10-01-2025                     | Transitioned the **CCP Connector** to General Availability (GA).    |
| 3.0.1       | 30-09-2024                     | Cisco Meraki via REST API configuration Changes pagination fix     |
| 3.0.0       | 27-12-2023                     | Initial Solution Release with new addition of **CCP Connector**                                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
