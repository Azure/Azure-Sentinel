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

The [1Password](https://www.1password.com) solution for Microsoft Sentinel enables you to ingest 1Password logs and events into Microsoft Sentinel. The connector provides visibility into 1Password Events and Alerts in Microsoft Sentinel to improve monitoring and investigation capabilities.



**Underlying Microsoft Technologies used:**



This solution takes a dependency on the following technologies, and some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs:



-  [Azure Functions](https://azure.microsoft.com/services/functions/#overview)

| | |
|--------------------------|---|
| **Tables Ingested** | `OnePasswordEventLogs_CL` |
| **Connector Definition Files** | [1Password_data_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Data%20Connectors/deployment/1Password_data_connector.json) |

[→ View full connector details](../connectors/1password.md)

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
| `OnePasswordEventLogs_CL` | 1Password, 1Password (Serverless) |

[← Back to Solutions Index](../solutions-index.md)
