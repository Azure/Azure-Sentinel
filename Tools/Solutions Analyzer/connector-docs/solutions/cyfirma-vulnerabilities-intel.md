# Cyfirma Vulnerabilities Intel

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-05-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CYFIRMA Vulnerabilities Intelligence](../connectors/cyfirmavulnerabilitiesinteldc.md)

**Publisher:** Microsoft

The CYFIRMA Vulnerabilities Intelligence data connector enables seamless log ingestion from the DeCYFIR API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the CYFIRMA API's to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Vulnerabilities Intelligence**

This connector provides the Vulnerabilities logs from CYFIRMA Vulnerabilities Intelligence. The connector uses the DeCYFIR API to retrieve logs and supports DCR-based ingestion time transformations, parsing security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **API Delta**: API Delta
- **Vendor-Associated Vulnerabilities**
- **Product-Associated Vulnerabilities**
- **Product with Version-Associated Vulnerabilities**
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `CyfirmaVulnerabilities_CL` |
| **Connector Definition Files** | [CyfirmaVulnerabilities_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Vulnerabilities%20Intel/Data%20Connectors/CyfirmaVulnerabilitiesIntel_ccp/CyfirmaVulnerabilities_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyfirmavulnerabilitiesinteldc.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyfirmaVulnerabilities_CL` | [CYFIRMA Vulnerabilities Intelligence](../connectors/cyfirmavulnerabilitiesinteldc.md) |

[← Back to Solutions Index](../solutions-index.md)
