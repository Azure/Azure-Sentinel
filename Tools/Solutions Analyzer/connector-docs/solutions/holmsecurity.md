# HolmSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Holm Security |
| **Support Tier** | Partner |
| **Support Link** | [https://support.holmsecurity.com/](https://support.holmsecurity.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HolmSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HolmSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Holm Security Asset Data](../connectors/holmsecurityassets.md)

**Publisher:** Holm Security

The connector provides the capability to poll data from Holm Security Center into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `net_assets_CL` |
| | `web_assets_CL` |
| **Connector Definition Files** | [HolmSecurityAssets_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HolmSecurity/Data%20Connectors/HolmSecurityAssets_API_FunctionApp.json) |

[→ View full connector details](../connectors/holmsecurityassets.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `net_assets_CL` | [Holm Security Asset Data](../connectors/holmsecurityassets.md) |
| `web_assets_CL` | [Holm Security Asset Data](../connectors/holmsecurityassets.md) |

[← Back to Solutions Index](../solutions-index.md)
