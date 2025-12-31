# Sophos Endpoint Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Sophos Endpoint Protection](../connectors/sophosep.md)
- [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SophosEPAlerts_CL`](../tables/sophosepalerts-cl.md) | [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md) | - |
| [`SophosEPEvents_CL`](../tables/sophosepevents-cl.md) | [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md) | - |
| [`SophosEP_CL`](../tables/sophosep-cl.md) | [Sophos Endpoint Protection](../connectors/sophosep.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SophosEPEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection/Parsers/SophosEPEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.6       | 23-10-2025                     | Updated the solution to be compatible with tool changes for the connection name.            |
| 3.0.5       | 21-08-2024                     | **Data Connector** [Sophos Endpoint Protection (using REST API)] Globally Available|
| 3.0.4       | 01-07-2024                     | Update files for CCP Connector to fix the connectivity|
| 3.0.3       | 25-04-2024                     | Repackaged for parser issue with old names       |
| 3.0.2       | 12-04-2024                     | Repackaged for parser fix in solution package 				|  
| 3.0.1       | 12-03-2024                     | Updated Sophos Endpoint **Function App** and **Parser** <br/>Added new CCP **Data Connector**		|  
| 3.0.0       | 14-08-2023                     | Manual deployment instructions updated for **Data Connector**		|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
