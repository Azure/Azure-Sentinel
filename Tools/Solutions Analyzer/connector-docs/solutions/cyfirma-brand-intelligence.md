# Cyfirma Brand Intelligence

## Solution Information

| | |
|------------------------|-------|
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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. CYFIRMA Brand Intelligence**

Connect to CYFIRMA Brand Intelligence to ingest alerts data into Microsoft Sentinel. This connector uses the DeCYFIR/DeTCT Alerts API to retrieve logs and supports DCR-based ingestion time transformations, parsing security data into custom tables during ingestion. This enhances performance and efficiency by eliminating the need for query-time parsing.
- **CYFIRMA API URL**: https://decyfir.cyfirma.com
- **CYFIRMA API Key**: (password field)
- **API Delta**: API Delta
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
