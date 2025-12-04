# Azure SQL Database solution for sentinel

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Azure SQL Databases

**Publisher:** Microsoft

Azure SQL is a fully managed, Platform-as-a-Service (PaaS) database engine that handles most database management functions, such as upgrading, patching, backups, and monitoring, without necessitating user involvement. This connector lets you stream your Azure SQL databases audit and diagnostic logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances.

**Tables Ingested:**

- `AzureDiagnostics`

**Connector Definition Files:**

- [template_AzureSql.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Data%20Connectors/template_AzureSql.JSON)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | Azure SQL Databases |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n