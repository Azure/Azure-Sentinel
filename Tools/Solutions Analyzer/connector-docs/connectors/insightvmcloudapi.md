# Rapid7 Insight Platform Vulnerability Management Reports

| | |
|----------|-------|
| **Connector ID** | `InsightVMCloudAPI` |
| **Publisher** | Rapid7 |
| **Tables Ingested** | [`NexposeInsightVMCloud_assets_CL`](../tables-index.md#nexposeinsightvmcloud_assets_cl), [`NexposeInsightVMCloud_vulnerabilities_CL`](../tables-index.md#nexposeinsightvmcloud_vulnerabilities_cl) |
| **Used in Solutions** | [Rapid7InsightVM](../solutions/rapid7insightvm.md) |
| **Connector Definition Files** | [InsightVMCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Rapid7InsightVM/Data%20Connectors/InsightVMCloud_API_FunctionApp.json) |

The [Rapid7 Insight VM](https://www.rapid7.com/products/insightvm/) Report data connector provides the capability to ingest Scan reports and vulnerability data into Microsoft Sentinel through the REST API from the  Rapid7 Insight platform (Managed in the cloud). Refer to [API documentation](https://docs.rapid7.com/insight/api-overview/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
