# Cyfirma Attack Surface

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-03-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md)

**Publisher:** Microsoft

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Attack Surface**

Connect to CYFIRMA Attack Surface to ingest alerts into Microsoft Sentinel. This connector uses the DeCYFIR/DeTCT API to retrieve logs and supports DCR-based ingestion time transformations, parsing security data into custom tables during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **API Delta**: API Delta
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `CyfirmaASCertificatesAlerts_CL` |
| | `CyfirmaASCloudWeaknessAlerts_CL` |
| | `CyfirmaASConfigurationAlerts_CL` |
| | `CyfirmaASDomainIPReputationAlerts_CL` |
| | `CyfirmaASDomainIPVulnerabilityAlerts_CL` |
| | `CyfirmaASOpenPortsAlerts_CL` |
| **Connector Definition Files** | [CyfirmaASAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Attack%20Surface/Data%20Connectors/CyfirmaASAlerts_ccp/CyfirmaASAlerts_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyfirmaattacksurfacealertsconnector.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyfirmaASCertificatesAlerts_CL` | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) |
| `CyfirmaASCloudWeaknessAlerts_CL` | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) |
| `CyfirmaASConfigurationAlerts_CL` | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) |
| `CyfirmaASDomainIPReputationAlerts_CL` | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) |
| `CyfirmaASDomainIPVulnerabilityAlerts_CL` | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) |
| `CyfirmaASOpenPortsAlerts_CL` | [CYFIRMA Attack Surface](../connectors/cyfirmaattacksurfacealertsconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
