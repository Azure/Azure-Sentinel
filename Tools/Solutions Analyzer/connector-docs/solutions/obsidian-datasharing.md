# Obsidian Datasharing

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Obsidian Security |
| **Support Tier** | Partner |
| **Support Link** | [https://obsidiansecurity.com/contact](https://obsidiansecurity.com/contact) |
| **Categories** | domains |
| **First Published** | 2024-01-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Obsidian%20Datasharing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Obsidian%20Datasharing) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Obsidian Datasharing Connector](../connectors/obsidiandatasharing.md)

**Publisher:** Obsidian Security

The Obsidian Datasharing connector provides the capability to read raw event data from Obsidian Datasharing in Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ObsidianActivity_CL` |
| | `ObsidianThreat_CL` |
| **Connector Definition Files** | [ObsidianDatasharing_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Obsidian%20Datasharing/Data%20Connectors/ObsidianDatasharing_CCP/ObsidianDatasharing_ConnectorDefinition.json) |

[→ View full connector details](../connectors/obsidiandatasharing.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ObsidianActivity_CL` | [Obsidian Datasharing Connector](../connectors/obsidiandatasharing.md) |
| `ObsidianThreat_CL` | [Obsidian Datasharing Connector](../connectors/obsidiandatasharing.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 25-09-2025                     | Initial Solution Release.                   |

[← Back to Solutions Index](../solutions-index.md)
