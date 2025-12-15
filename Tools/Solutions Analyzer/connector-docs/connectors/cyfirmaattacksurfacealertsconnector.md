# CYFIRMA Attack Surface

| | |
|----------|-------|
| **Connector ID** | `CyfirmaAttackSurfaceAlertsConnector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CyfirmaASCertificatesAlerts_CL`](../tables-index.md#cyfirmaascertificatesalerts_cl), [`CyfirmaASCloudWeaknessAlerts_CL`](../tables-index.md#cyfirmaascloudweaknessalerts_cl), [`CyfirmaASConfigurationAlerts_CL`](../tables-index.md#cyfirmaasconfigurationalerts_cl), [`CyfirmaASDomainIPReputationAlerts_CL`](../tables-index.md#cyfirmaasdomainipreputationalerts_cl), [`CyfirmaASDomainIPVulnerabilityAlerts_CL`](../tables-index.md#cyfirmaasdomainipvulnerabilityalerts_cl), [`CyfirmaASOpenPortsAlerts_CL`](../tables-index.md#cyfirmaasopenportsalerts_cl) |
| **Used in Solutions** | [Cyfirma Attack Surface](../solutions/cyfirma-attack-surface.md) |
| **Connector Definition Files** | [CyfirmaASAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Data%20Connectors/CyfirmaASAlerts_ccp/CyfirmaASAlerts_DataConnectorDefinition.json) |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Attack Surface**

Connect to CYFIRMA Attack Surface to ingest alerts into Microsoft Sentinel. This connector uses the DeCYFIR/DeTCT API to retrieve logs and supports DCR-based ingestion time transformations, parsing security data into custom tables during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **API Delta**: API Delta
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
