# CYFIRMA Digital Risk

| | |
|----------|-------|
| **Connector ID** | `CyfirmaDigitalRiskAlertsConnector` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Cyfirma Digital Risk](../solutions/cyfirma-digital-risk.md) |
| **Connector Definition Files** | [CyfirmaDigitalRiskAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Data%20Connectors/CyfirmaDigitalRiskAlerts_ccp/CyfirmaDigitalRiskAlerts_DataConnectorDefinition.json) |

The CYFIRMA Digital Risk Alerts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`CyfirmaDBWMDarkWebAlerts_CL`](../tables/cyfirmadbwmdarkwebalerts-cl.md) | — | — |
| [`CyfirmaDBWMPhishingAlerts_CL`](../tables/cyfirmadbwmphishingalerts-cl.md) | — | — |
| [`CyfirmaDBWMRansomwareAlerts_CL`](../tables/cyfirmadbwmransomwarealerts-cl.md) | — | — |
| [`CyfirmaSPEConfidentialFilesAlerts_CL`](../tables/cyfirmaspeconfidentialfilesalerts-cl.md) | — | — |
| [`CyfirmaSPEPIIAndCIIAlerts_CL`](../tables/cyfirmaspepiiandciialerts-cl.md) | — | — |
| [`CyfirmaSPESocialThreatAlerts_CL`](../tables/cyfirmaspesocialthreatalerts-cl.md) | — | — |
| [`CyfirmaSPESourceCodeAlerts_CL`](../tables/cyfirmaspesourcecodealerts-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Digital Risk**

Connect to CYFIRMA Digital Risk Alerts to ingest logs into Microsoft Sentinel. This connector uses the DeCYFIR/DeTCT API to retrieve alerts and supports DCR-based ingestion time transformations for efficient log parsing.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **API Delta**: API Delta
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
