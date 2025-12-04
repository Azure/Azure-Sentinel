# Box

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### Box

**Publisher:** Box

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

**Tables Ingested:**

- `BoxEvents_CL`

**Connector Definition Files:**

- [Box_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Data%20Connectors/Box_API_FunctionApp.json)

### Box Events (CCP)

**Publisher:** Microsoft

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

**Tables Ingested:**

- `BoxEventsV2_CL`
- `BoxEvents_CL`

**Connector Definition Files:**

- [BoxEvents_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Data%20Connectors/BoxEvents_ccp/BoxEvents_DataConnectorDefinition.json)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BoxEventsV2_CL` | Box Events (CCP) |
| `BoxEvents_CL` | Box, Box Events (CCP) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n