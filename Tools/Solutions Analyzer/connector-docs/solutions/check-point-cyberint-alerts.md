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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Check Point Cyberint API Key, Argos URL, and Customer Name**: The connector API key, Argos URL, and Customer Name are required

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Checkpoint Cyberint Alerts to Microsoft Sentinel**

To enable the connector provide the required information below and click on Connect.
>
- **Argos URL**: Argos URL
- **API Token**: (password field)
- **Customer Name**: Customer Name
- Click 'Connect' to establish connection

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
