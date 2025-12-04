# 1Password

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | 1Password |
| **Support Tier** | Partner |
| **Support Link** | [https://support.1password.com/](https://support.1password.com/) |
| **Categories** | domains |
| **First Published** | 2023-12-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [1Password](../connectors/1password.md)

**Publisher:** 1Password

### [1Password (Serverless)](../connectors/1passwordccpdefinition.md)

**Publisher:** 1Password

The 1Password CCP connector allows the user to ingest 1Password Audit, Signin & ItemUsage events into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `OnePasswordEventLogs_CL` |
| **Connector Definition Files** | [1Password_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Data%20Connectors/1Password_ccpv2/1Password_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/1passwordccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OnePasswordEventLogs_CL` | [1Password](../connectors/1password.md), [1Password (Serverless)](../connectors/1passwordccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
