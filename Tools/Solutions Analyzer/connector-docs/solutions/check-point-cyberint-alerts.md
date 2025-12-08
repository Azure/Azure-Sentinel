# Check Point Cyberint Alerts

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cyberint |
| **Support Tier** | Partner |
| **Support Link** | [https://cyberint.com/customer-support/](https://cyberint.com/customer-support/) |
| **Categories** | domains |
| **First Published** | 2025-03-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20Alerts) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Check Point Cyberint Alerts Connector (via Codeless Connector Platform)](../connectors/checkpointcyberintalerts.md)

**Publisher:** Checkpoint Cyberint

Cyberint, a Check Point company, provides a Microsoft Sentinel integration to streamline critical Alerts and bring enriched threat intelligence from the Infinity External Risk Management solution into Microsoft Sentinel. This simplifies the process of tracking the status of tickets with automatic sync updates across systems. Using this new integration for Microsoft Sentinel, existing Cyberint and Microsoft Sentinel customers can easily pull logs based on Cyberint's findings into Microsoft Sentinel platform.

| | |
|--------------------------|---|
| **Tables Ingested** | `argsentdc_CL` |
| **Connector Definition Files** | [CyberintArgosAlertsLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20Alerts/Data%20Connectors/CyberintArgosAlertsLogs_ccp/CyberintArgosAlertsLogs_connectorDefinition.json) |

[→ View full connector details](../connectors/checkpointcyberintalerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `argsentdc_CL` | [Check Point Cyberint Alerts Connector (via Codeless Connector Platform)](../connectors/checkpointcyberintalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
