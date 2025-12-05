# NonameSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Noname Security |
| **Support Tier** | Partner |
| **Support Link** | [https://nonamesecurity.com/](https://nonamesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2022-12-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NonameSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NonameSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Noname Security for Microsoft Sentinel](../connectors/nonamesecuritymicrosoftsentinel.md)

**Publisher:** Noname Security

Noname Security solution to POST data into a Microsoft Sentinel SIEM workspace via the Azure Monitor REST API

| | |
|--------------------------|---|
| **Tables Ingested** | `NonameAPISecurityAlert_CL` |
| **Connector Definition Files** | [Connector_RESTAPI_NonameSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NonameSecurity/Data%20Connectors/Connector_RESTAPI_NonameSecurity.json) |

[→ View full connector details](../connectors/nonamesecuritymicrosoftsentinel.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NonameAPISecurityAlert_CL` | [Noname Security for Microsoft Sentinel](../connectors/nonamesecuritymicrosoftsentinel.md) |

[← Back to Solutions Index](../solutions-index.md)
