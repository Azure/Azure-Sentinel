# Box

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Box](../connectors/boxdataconnector.md)

**Publisher:** Box

### [Box Events (CCP)](../connectors/boxeventsccpdefinition.md)

**Publisher:** Microsoft

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `BoxEventsV2_CL` |
| | `BoxEvents_CL` |
| **Connector Definition Files** | [BoxEvents_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Data%20Connectors/BoxEvents_ccp/BoxEvents_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/boxeventsccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BoxEventsV2_CL` | [Box Events (CCP)](../connectors/boxeventsccpdefinition.md) |
| `BoxEvents_CL` | [Box](../connectors/boxdataconnector.md), [Box Events (CCP)](../connectors/boxeventsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
