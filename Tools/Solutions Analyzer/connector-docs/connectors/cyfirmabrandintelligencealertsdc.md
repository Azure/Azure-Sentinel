# CYFIRMA Brand Intelligence

| | |
|----------|-------|
| **Connector ID** | `CyfirmaBrandIntelligenceAlertsDC` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Cyfirma Brand Intelligence](../solutions/cyfirma-brand-intelligence.md) |
| **Connector Definition Files** | [CyfirmaBIAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Data%20Connectors/CyfirmaBIAlerts_ccp/CyfirmaBIAlerts_DataConnectorDefinition.json) |

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`CyfirmaBIDomainITAssetAlerts_CL`](../tables/cyfirmabidomainitassetalerts-cl.md) | — | — |
| [`CyfirmaBIExecutivePeopleAlerts_CL`](../tables/cyfirmabiexecutivepeoplealerts-cl.md) | — | — |
| [`CyfirmaBIMaliciousMobileAppsAlerts_CL`](../tables/cyfirmabimaliciousmobileappsalerts-cl.md) | — | — |
| [`CyfirmaBIProductSolutionAlerts_CL`](../tables/cyfirmabiproductsolutionalerts-cl.md) | — | — |
| [`CyfirmaBISocialHandlersAlerts_CL`](../tables/cyfirmabisocialhandlersalerts-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Brand Intelligence**

Connect to CYFIRMA Brand Intelligence to ingest alerts data into Microsoft Sentinel. This connector uses the DeCYFIR/DeTCT Alerts API to retrieve logs and supports DCR-based ingestion time transformations, parsing security data into custom tables during ingestion. This enhances performance and efficiency by eliminating the need for query-time parsing.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **API Delta**: API Delta
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
