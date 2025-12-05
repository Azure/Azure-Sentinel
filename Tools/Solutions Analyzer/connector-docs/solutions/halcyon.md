# Halcyon

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Halcyon |
| **Support Tier** | Community |
| **Support Link** | [https://www.halcyon.ai](https://www.halcyon.ai) |
| **Categories** | domains |
| **First Published** | 2025-10-15 |
| **Last Updated** | 2025-10-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Halcyon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Halcyon) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Halcyon Connector](../connectors/halcyonpush.md)

**Publisher:** Halcyon

The [Halcyon](https://www.halcyon.ai) connector provides the capability to send data from Halcyon to Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `HalcyonAuthenticationEvents_CL` |
| | `HalcyonDnsActivity_CL` |
| | `HalcyonFileActivity_CL` |
| | `HalcyonNetworkSession_CL` |
| | `HalcyonProcessEvent_CL` |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Halcyon/Data%20Connectors/Halcyon_ccp/connectorDefinition.json) |

[→ View full connector details](../connectors/halcyonpush.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `HalcyonAuthenticationEvents_CL` | [Halcyon Connector](../connectors/halcyonpush.md) |
| `HalcyonDnsActivity_CL` | [Halcyon Connector](../connectors/halcyonpush.md) |
| `HalcyonFileActivity_CL` | [Halcyon Connector](../connectors/halcyonpush.md) |
| `HalcyonNetworkSession_CL` | [Halcyon Connector](../connectors/halcyonpush.md) |
| `HalcyonProcessEvent_CL` | [Halcyon Connector](../connectors/halcyonpush.md) |

[← Back to Solutions Index](../solutions-index.md)
