# Trend Micro Cloud App Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Trend Micro Cloud App Security](../connectors/trendmicrocas.md)

**Publisher:** Trend Micro

The [Trend Micro Cloud App Security](https://www.trendmicro.com/en_be/business/products/user-protection/sps/email-and-collaboration/cloud-app-security.html) data connector provides the capability to retrieve security event logs of the services that Cloud App Security protects and more events into Microsoft Sentinel through the Log Retrieval API. Refer to API [documentation](https://docs.trendmicro.com/en-us/enterprise/cloud-app-security-integration-api-online-help/supported-cloud-app-/log-retrieval-api/get-security-logs.aspx) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `TrendMicroCAS_CL` |
| **Connector Definition Files** | [TerndMicroCAS_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Data%20Connectors/TerndMicroCAS_API_FunctionApp.json) |

[→ View full connector details](../connectors/trendmicrocas.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `TrendMicroCAS_CL` | [Trend Micro Cloud App Security](../connectors/trendmicrocas.md) |

[← Back to Solutions Index](../solutions-index.md)
