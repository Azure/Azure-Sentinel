# Cyble Vision

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cyble Support |
| **Support Tier** | Partner |
| **Support Link** | [https://cyble.com/talk-to-sales/](https://cyble.com/talk-to-sales/) |
| **Categories** | domains |
| **First Published** | 2025-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cyble Vision Alerts](../connectors/cyblevisionalerts.md)

**Publisher:** Cyble

The **Cyble Vision Alerts** CCF Data Connector enables Ingestion of Threat Alerts from Cyble Vision into Microsoft Sentinel using the Codeless Connector Framework Connector. It collects alert data via API, normalizes it, and stores it in a custom table for advanced detection, correlation, and response.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CybleVisionAlerts_CL` |
| **Connector Definition Files** | [CybleVisionAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Data%20Connectors/CybleVisionAlerts_CCF/CybleVisionAlerts_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyblevisionalerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CybleVisionAlerts_CL` | [Cyble Vision Alerts](../connectors/cyblevisionalerts.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
| 3.0.2       | 14-12-2025                     | Added new **CCF data connector**.<br/> Added new **Parsers** to Parse data message of each service.<br/> Added **Analytic Rules** to generate incidents based on Services.                      |
| 3.0.1       | 10-06-2025                     | *Cyble-ThreatIntelligence-Ingest* **Playbook**, including fixes for de-duplication of IoCs, optimized KQL query load, and pagination support. |
| 3.0.0       | 20-05-2025                     | Initial Solution Release.                              |

[← Back to Solutions Index](../solutions-index.md)
