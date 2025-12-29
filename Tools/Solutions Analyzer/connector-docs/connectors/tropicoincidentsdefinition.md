# Tropico Security - Incidents

| | |
|----------|-------|
| **Connector ID** | `TropicoIncidentsDefinition` |
| **Publisher** | Tropico Security |
| **Tables Ingested** | [`{{graphQueriesTableName}}`](../tables-index.md#{{graphqueriestablename}}) |
| **Used in Solutions** | [Tropico](../solutions/tropico.md) |
| **Connector Definition Files** | [TropicoIncidents_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico/Data%20Connectors/TropicoIncidents_CCF/TropicoIncidents_ConnectorDefinition.json) |

Ingest attacker session incidents from Tropico Security Platform.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and write permissions required

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Tropico Security Platform**

Enter your read-only API key from Tropico Settings.
- **API Key**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
