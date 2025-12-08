# Digital Shadows

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Digital Shadows |
| **Support Tier** | Partner |
| **Support Link** | [https://www.digitalshadows.com/](https://www.digitalshadows.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Digital Shadows Searchlight](../connectors/digitalshadowssearchlightazurefunctions.md)

**Publisher:** Digital Shadows

The Digital Shadows data connector provides ingestion of the incidents and alerts from Digital Shadows Searchlight into the Microsoft Sentinel using the REST API. The connector will provide the incidents and alerts information such that it helps to examine, diagnose and analyse the potential security risks and threats.

| | |
|--------------------------|---|
| **Tables Ingested** | `DigitalShadows_CL` |
| **Connector Definition Files** | [DigitalShadowsSearchlight_API_functionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Data%20Connectors/Digital%20Shadows/DigitalShadowsSearchlight_API_functionApp.json) |

[→ View full connector details](../connectors/digitalshadowssearchlightazurefunctions.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DigitalShadows_CL` | [Digital Shadows Searchlight](../connectors/digitalshadowssearchlightazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
