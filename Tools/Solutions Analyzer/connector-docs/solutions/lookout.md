# Lookout

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Lookout |
| **Support Tier** | Partner |
| **Support Link** | [https://www.lookout.com/support](https://www.lookout.com/support) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Lookout](../connectors/lookoutapi.md)

**Publisher:** Lookout

### [Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)](../connectors/lookoutstreaming-definition.md)

**Publisher:** Microsoft

The [Lookout Mobile Threat Detection](https://lookout.com) data connector provides the capability to ingest events related to mobile security risks into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. This connector helps you examine potential security risks detected in mobile devices.

| | |
|--------------------------|---|
| **Tables Ingested** | `LookoutMtdV2_CL` |
| **Connector Definition Files** | [LookoutStreaming_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Data%20Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/lookoutstreaming-definition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `LookoutMtdV2_CL` | [Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)](../connectors/lookoutstreaming-definition.md) |
| `Lookout_CL` | [[DEPRECATED] Lookout](../connectors/lookoutapi.md) |

[← Back to Solutions Index](../solutions-index.md)
