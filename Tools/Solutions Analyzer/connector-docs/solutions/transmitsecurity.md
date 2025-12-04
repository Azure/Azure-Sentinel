# TransmitSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Transmit Security |
| **Support Tier** | Partner |
| **Support Link** | [https://transmitsecurity.com/support](https://transmitsecurity.com/support) |
| **Categories** | domains |
| **First Published** | 2024-06-10 |
| **Last Updated** | 2024-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Transmit Security Connector](../connectors/transmitsecurity.md)

**Publisher:** TransmitSecurity

The [Transmit Security] data connector provides the capability to ingest common Transmit Security API events into Microsoft Sentinel through the REST API. [Refer to API documentation for more information](https://developer.transmitsecurity.com/). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `TransmitSecurityActivity_CL` |
| **Connector Definition Files** | [TransmitSecurity_API_FunctionApp.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity/Data%20Connectors/TransmitSecurity_API_FunctionApp.JSON) |

[→ View full connector details](../connectors/transmitsecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `TransmitSecurityActivity_CL` | [Transmit Security Connector](../connectors/transmitsecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
