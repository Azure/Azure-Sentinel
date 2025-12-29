# Anvilogic

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Anvilogic |
| **Support Tier** | Partner |
| **Support Link** | [https://www.anvilogic.com/](https://www.anvilogic.com/) |
| **Categories** | domains |
| **First Published** | 2025-06-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Anvilogic](../connectors/anvilogicccfdefinition.md)

**Publisher:** Anvilogic

The Anvilogic data connector allows you to pull events of interest generated in the Anvilogic ADX cluster into your Microsoft Sentinel

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Anvilogic_Alerts_CL` |
| **Connector Definition Files** | [Anvilogic_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic/Data%20Connectors/AnviLogic_CCF/Anvilogic_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/anvilogicccfdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Anvilogic_Alerts_CL` | [Anvilogic](../connectors/anvilogicccfdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                           |
|-------------|--------------------------------|--------------------------------------------------------------|
| 3.0.0       | 20-06-2025                     | Initial Solution Release.                                    |

[← Back to Solutions Index](../solutions-index.md)
