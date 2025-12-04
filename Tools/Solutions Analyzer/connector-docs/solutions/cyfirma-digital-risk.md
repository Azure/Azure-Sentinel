# Cyfirma Digital Risk

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-03-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md)

**Publisher:** Microsoft

The CYFIRMA Digital Risk Alerts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyfirmaDBWMDarkWebAlerts_CL` |
| | `CyfirmaDBWMPhishingAlerts_CL` |
| | `CyfirmaDBWMRansomwareAlerts_CL` |
| | `CyfirmaSPEConfidentialFilesAlerts_CL` |
| | `CyfirmaSPEPIIAndCIIAlerts_CL` |
| | `CyfirmaSPESocialThreatAlerts_CL` |
| | `CyfirmaSPESourceCodeAlerts_CL` |
| **Connector Definition Files** | [CyfirmaDigitalRiskAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Data%20Connectors/CyfirmaDigitalRiskAlerts_ccp/CyfirmaDigitalRiskAlerts_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyfirmadigitalriskalertsconnector.md)

## Tables Reference

This solution ingests data into **7 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyfirmaDBWMDarkWebAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |
| `CyfirmaDBWMPhishingAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |
| `CyfirmaDBWMRansomwareAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |
| `CyfirmaSPEConfidentialFilesAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |
| `CyfirmaSPEPIIAndCIIAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |
| `CyfirmaSPESocialThreatAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |
| `CyfirmaSPESourceCodeAlerts_CL` | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
