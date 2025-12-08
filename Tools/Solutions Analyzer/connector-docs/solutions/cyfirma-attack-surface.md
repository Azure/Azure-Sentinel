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
