# DruvaDataSecurityCloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Druva Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://support.druva.com/](https://support.druva.com/) |
| **Categories** | domains |
| **First Published** | 2024-12-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Druva Events Connector](../connectors/druvaeventccpdefinition.md)

**Publisher:** Microsoft

Provides capability to ingest the Druva events from Druva APIs

| | |
|--------------------------|---|
| **Tables Ingested** | `DruvaInsyncEvents_CL` |
| | `DruvaPlatformEvents_CL` |
| | `DruvaSecurityEvents_CL` |
| **Connector Definition Files** | [Druva_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Data%20Connectors/Druva_ccp/Druva_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/druvaeventccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DruvaInsyncEvents_CL` | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) |
| `DruvaPlatformEvents_CL` | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) |
| `DruvaSecurityEvents_CL` | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
