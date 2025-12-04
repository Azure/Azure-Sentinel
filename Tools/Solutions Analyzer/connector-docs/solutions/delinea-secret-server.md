# Delinea Secret Server

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Delinea |
| **Support Tier** | Partner |
| **Support Link** | [https://delinea.com/support/](https://delinea.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Delinea Secret Server via AMA

**Publisher:** Delinea, Inc

Common Event Format (CEF) from Delinea Secret Server 

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_DelineaSecretServerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/template_DelineaSecretServerAMA.json)

### [Deprecated] Delinea Secret Server via Legacy Agent

**Publisher:** Delinea, Inc

Common Event Format (CEF) from Delinea Secret Server 

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [DelineaSecretServer_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/DelineaSecretServer_CEF.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n