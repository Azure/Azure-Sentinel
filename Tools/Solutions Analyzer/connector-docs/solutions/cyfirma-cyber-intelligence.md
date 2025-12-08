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
