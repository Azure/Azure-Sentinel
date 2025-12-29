# Palo Alto Cortex Xpanse CCF

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-12-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Palo Alto Cortex Xpanse (via Codeless Connector Framework)](../connectors/paloaltoexpanseccpdefinition.md)

**Publisher:** Microsoft

The Palo Alto Cortex Xpanse data connector ingests alerts data into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CortexXpanseAlerts_CL` |
| **Connector Definition Files** | [CortexXpanse_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20Xpanse%20CCF/Data%20Connectors/CortexXpanse_ccp/CortexXpanse_ConnectorDefinition.json) |

[→ View full connector details](../connectors/paloaltoexpanseccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CortexXpanseAlerts_CL` | [Palo Alto Cortex Xpanse (via Codeless Connector Framework)](../connectors/paloaltoexpanseccpdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.1       | 07-10-2025                     | Palo Alto Cortex Xpanse CCF **Data Connector** Moving to GA. |
| 3.0.0       | 04-08-2025                     | Initial Solution Release. <br/>New CCF **Data Connector** 'Palo Alto Cortex Xpanse CCF'.                                                |

[← Back to Solutions Index](../solutions-index.md)
