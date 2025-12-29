# Tropico

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

Ingest security alerts from Tropico Security Platform in OCSF Security Finding format.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `{{graphQueriesTableName}}` |
| **Connector Definition Files** | [TropicoAlerts_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico/Data%20Connectors/TropicoAlerts_CCF/TropicoAlerts_ConnectorDefinition.json) |

[→ View full connector details](../connectors/tropicoalertsdefinition.md)

### [Tropico Security - Events](../connectors/tropicoeventsdefinition.md)

**Publisher:** Tropico Security

Ingest security events from Tropico Security Platform in OCSF Security Finding format.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `{{graphQueriesTableName}}` |
| **Connector Definition Files** | [TropicoEvents_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico/Data%20Connectors/TropicoEvents_CCF/TropicoEvents_ConnectorDefinition.json) |

[→ View full connector details](../connectors/tropicoeventsdefinition.md)

### [Tropico Security - Incidents](../connectors/tropicoincidentsdefinition.md)

**Publisher:** Tropico Security

Ingest attacker session incidents from Tropico Security Platform.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `{{graphQueriesTableName}}` |
| **Connector Definition Files** | [TropicoIncidents_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tropico/Data%20Connectors/TropicoIncidents_CCF/TropicoIncidents_ConnectorDefinition.json) |

[→ View full connector details](../connectors/tropicoincidentsdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `{{graphQueriesTableName}}` | [Tropico Security - Alerts](../connectors/tropicoalertsdefinition.md), [Tropico Security - Events](../connectors/tropicoeventsdefinition.md), [Tropico Security - Incidents](../connectors/tropicoincidentsdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 02-12-2025                     | Initial release  |

[← Back to Solutions Index](../solutions-index.md)
