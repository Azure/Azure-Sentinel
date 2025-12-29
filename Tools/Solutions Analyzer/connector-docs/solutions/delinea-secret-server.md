# Delinea Secret Server

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Delinea |
| **Support Tier** | Partner |
| **Support Link** | [https://delinea.com/support/](https://delinea.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md)

**Publisher:** Delinea, Inc

Common Event Format (CEF) from Delinea Secret Server 

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_DelineaSecretServerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/template_DelineaSecretServerAMA.json) |

[→ View full connector details](../connectors/delineasecretserverama.md)

### [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md)

**Publisher:** Delinea, Inc

Common Event Format (CEF) from Delinea Secret Server 

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [DelineaSecretServer_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/DelineaSecretServer_CEF.json) |

[→ View full connector details](../connectors/delineasecretserver-cef.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md), [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 20-09-2023                     |	Addition of new Delinea Secret Server AMA **Data Connector**    |

[← Back to Solutions Index](../solutions-index.md)
