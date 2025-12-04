# Rapid7InsightVM

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Rapid7 Insight Platform Vulnerability Management Reports](../connectors/insightvmcloudapi.md)

**Publisher:** Rapid7

The [Rapid7 Insight VM](https://www.rapid7.com/products/insightvm/) Report data connector provides the capability to ingest Scan reports and vulnerability data into Microsoft Sentinel through the REST API from the  Rapid7 Insight platform (Managed in the cloud). Refer to [API documentation](https://docs.rapid7.com/insight/api-overview/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `NexposeInsightVMCloud_assets_CL` |
| | `NexposeInsightVMCloud_vulnerabilities_CL` |
| **Connector Definition Files** | [InsightVMCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM/Data%20Connectors/InsightVMCloud_API_FunctionApp.json) |

[→ View full connector details](../connectors/insightvmcloudapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NexposeInsightVMCloud_assets_CL` | [Rapid7 Insight Platform Vulnerability Management Reports](../connectors/insightvmcloudapi.md) |
| `NexposeInsightVMCloud_vulnerabilities_CL` | [Rapid7 Insight Platform Vulnerability Management Reports](../connectors/insightvmcloudapi.md) |

[← Back to Solutions Index](../solutions-index.md)
