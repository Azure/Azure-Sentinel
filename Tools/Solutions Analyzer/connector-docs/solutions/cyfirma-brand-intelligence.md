# Cyfirma Brand Intelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-03-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md)

**Publisher:** Microsoft

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CyfirmaBIDomainITAssetAlerts_CL` |
| | `CyfirmaBIExecutivePeopleAlerts_CL` |
| | `CyfirmaBIMaliciousMobileAppsAlerts_CL` |
| | `CyfirmaBIProductSolutionAlerts_CL` |
| | `CyfirmaBISocialHandlersAlerts_CL` |
| **Connector Definition Files** | [CyfirmaBIAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Brand%20Intelligence/Data%20Connectors/CyfirmaBIAlerts_ccp/CyfirmaBIAlerts_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyfirmabrandintelligencealertsdc.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyfirmaBIDomainITAssetAlerts_CL` | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) |
| `CyfirmaBIExecutivePeopleAlerts_CL` | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) |
| `CyfirmaBIMaliciousMobileAppsAlerts_CL` | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) |
| `CyfirmaBIProductSolutionAlerts_CL` | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) |
| `CyfirmaBISocialHandlersAlerts_CL` | [CYFIRMA Brand Intelligence](../connectors/cyfirmabrandintelligencealertsdc.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.3       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.2       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.1       | 17-06-2025                     | Minor changes to **CCF Data Connector**.                               |
| 3.0.0       | 14-04-2025                     | Initial Solution Release.                                              |

[← Back to Solutions Index](../solutions-index.md)
