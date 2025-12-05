# CYFIRMA Vulnerabilities Intelligence

| | |
|----------|-------|
| **Connector ID** | `CyfirmaVulnerabilitiesIntelDC` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CyfirmaVulnerabilities_CL`](../tables-index.md#cyfirmavulnerabilities_cl) |
| **Used in Solutions** | [Cyfirma Vulnerabilities Intel](../solutions/cyfirma-vulnerabilities-intel.md) |
| **Connector Definition Files** | [CyfirmaVulnerabilities_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel/Data%20Connectors/CyfirmaVulnerabilitiesIntel_ccp/CyfirmaVulnerabilities_DataConnectorDefinition.json) |

The CYFIRMA Vulnerabilities Intelligence data connector enables seamless log ingestion from the DeCYFIR API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the CYFIRMA API's to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[← Back to Connectors Index](../connectors-index.md)
