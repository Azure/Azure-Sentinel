# Tropico

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | TROPICO Security |
| **Support Tier** | Partner |
| **Support Link** | [https://tropicosecurity.com/](https://tropicosecurity.com/) |
| **Categories** | domains |
| **First Published** | 2025-12-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Tropico Security - Alerts](../connectors/tropicoalertsdefinition.md)

**Publisher:** Tropico Security

### [Tropico Security - Events](../connectors/tropicoeventsdefinition.md)

**Publisher:** Tropico Security

### [Tropico Security - Incidents](../connectors/tropicoincidentsdefinition.md)

**Publisher:** Tropico Security

Ingest attacker session incidents from Tropico Security Platform.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and write permissions required

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Tropico Security Platform**

Enter your read-only API key from Tropico Settings.
- **API Key**: (password field)
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `{{graphQueriesTableName}}` |
| **Connector Definition Files** | [TropicoIncidents_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico/Data%20Connectors/TropicoIncidents_CCF/TropicoIncidents_ConnectorDefinition.json) |

[→ View full connector details](../connectors/tropicoincidentsdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `{{graphQueriesTableName}}` | [Tropico Security - Alerts](../connectors/tropicoalertsdefinition.md), [Tropico Security - Events](../connectors/tropicoeventsdefinition.md), [Tropico Security - Incidents](../connectors/tropicoincidentsdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
