# Cyfirma Attack Surface

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
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

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.3       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.2       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.1       | 17-06-2025                     | Minor changes to **CCF Data Connector**.                               |
| 3.0.0       | 14-04-2025                     | Initial Solution Release.                                              |

[← Back to Solutions Index](../solutions-index.md)
