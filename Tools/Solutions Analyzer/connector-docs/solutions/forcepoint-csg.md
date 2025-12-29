# Forcepoint CSG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [ForcepointCloudSecurityGateway.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/ForcepointCloudSecurityGateway.json) |

[→ View full connector details](../connectors/forcepointcsg.md)

### [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md)

**Publisher:** Forcepoint

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ForcepointCloudSecurityGatewayAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/template_ForcepointCloudSecurityGatewayAMA.json) |

[→ View full connector details](../connectors/forcepointcsgama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint CSG via AMA](../connectors/forcepointcsgama.md), [[Deprecated] Forcepoint CSG via Legacy Agent](../connectors/forcepointcsg.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 19-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.2       | 15-07-2024                     |	Deprecating data connectors                                     |
| 3.0.1       | 19-12-2023                     |	Workbook moved from standalone to solution and repackage        |
| 3.0.0       | 11-09-2023                     |	Addition of new Forcepoint CSG AMA **Data Connector**           |

[← Back to Solutions Index](../solutions-index.md)
