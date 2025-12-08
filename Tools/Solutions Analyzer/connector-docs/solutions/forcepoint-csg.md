# Forcepoint CSG

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md)

**Publisher:** Forcepoint

### [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md)

**Publisher:** Forcepoint

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ForcepointCloudSecurityGatewayAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/template_ForcepointCloudSecurityGatewayAMA.json) |

[→ View full connector details](../connectors/forcepointcsgama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md), [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md) |

[← Back to Solutions Index](../solutions-index.md)
