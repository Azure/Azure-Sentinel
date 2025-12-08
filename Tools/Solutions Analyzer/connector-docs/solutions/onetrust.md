# OneTrust

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | OneTrust, LLC |
| **Support Tier** | Partner |
| **Support Link** | [https://www.onetrust.com/support/](https://www.onetrust.com/support/) |
| **Categories** | domains |
| **First Published** | 2025-10-24 |
| **Last Updated** | 2025-10-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneTrust](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneTrust) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [OneTrust](../connectors/onetrustpush.md)

**Publisher:** OneTrust

The OneTrust connector for Microsoft Sentinel provides the capability to have near real time visibility into where sensitive data has been located or remediated across across Google Cloud and other OneTrust supported data sources.

| | |
|--------------------------|---|
| **Tables Ingested** | `OneTrustMetadataV3_CL` |
| **Connector Definition Files** | [OneTrustLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneTrust/Data%20Connectors/OneTrustLogs_CCF/OneTrustLogs_connectorDefinition.json) |

[→ View full connector details](../connectors/onetrustpush.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OneTrustMetadataV3_CL` | [OneTrust](../connectors/onetrustpush.md) |

[← Back to Solutions Index](../solutions-index.md)
