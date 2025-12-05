# Delinea Secret Server

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md)

**Publisher:** Delinea, Inc

Common Event Format (CEF) from Delinea Secret Server 

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [DelineaSecretServer_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/DelineaSecretServer_CEF.json) |

[→ View full connector details](../connectors/delineasecretserver-cef.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Delinea Secret Server via AMA](../connectors/delineasecretserverama.md), [[Deprecated] Delinea Secret Server via Legacy Agent](../connectors/delineasecretserver-cef.md) |

[← Back to Solutions Index](../solutions-index.md)
