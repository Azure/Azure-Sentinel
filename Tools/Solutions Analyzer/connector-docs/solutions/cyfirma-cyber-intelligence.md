# Cyfirma Cyber Intelligence

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-05-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md)

**Publisher:** Microsoft

The CYFIRMA Cyber Intelligence data connector enables seamless log ingestion from the DeCYFIR API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Cyber Intelligence**

This connector provides the Indicators, Threat actors, Malware and Campaigns logs from CYFIRMA Cyber Intelligence. The connector uses the DeCYFIR API to retrieve logs and supports DCR-based ingestion time transformations, parsing security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **Pull all IoC's Or Tailored IoC's**: All IoC's or Tailored IoC's
- **API Delta**: API Delta
- **Recommended Actions**: Recommended Action can be any one of:All/Monitor/Block
- **Threat Actor Associated**: Is any Threat Actor Associated with the IoC's
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `CyfirmaCampaigns_CL` |
| | `CyfirmaIndicators_CL` |
| | `CyfirmaMalware_CL` |
| | `CyfirmaThreatActors_CL` |
| **Connector Definition Files** | [CyfirmaCyberIntel_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Data%20Connectors/CyfirmaCyberIntelligence_ccp/CyfirmaCyberIntel_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyfirmacyberintelligencedc.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyfirmaCampaigns_CL` | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) |
| `CyfirmaIndicators_CL` | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) |
| `CyfirmaMalware_CL` | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) |
| `CyfirmaThreatActors_CL` | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) |

[← Back to Solutions Index](../solutions-index.md)
