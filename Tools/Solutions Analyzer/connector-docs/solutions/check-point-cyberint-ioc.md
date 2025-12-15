# Check Point Cyberint IOC

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cyberint |
| **Support Tier** | Partner |
| **Support Link** | [https://cyberint.com/customer-support/](https://cyberint.com/customer-support/) |
| **Categories** | domains |
| **First Published** | 2025-04-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20IOC) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Check Point Cyberint IOC Connector](../connectors/checkpointcyberintioc.md)

**Publisher:** Checkpoint Cyberint

This is data connector for Check Point Cyberint IOC.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Check Point Cyberint API Key and Argos URL**: The connector API key and Argos URL are required

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Checkpoint Cyberint Alerts to Microsoft Sentinel**

To enable the connector provide the required information below and click on Connect.
>
- **Argos URL**: Argos URL
- **API key**: API key
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `iocsent_CL` |
| **Connector Definition Files** | [CyberintArgosIOCLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20Cyberint%20IOC/Data%20Connectors/CyberintArgosIOCLogs_ccp/CyberintArgosIOCLogs_connectorDefinition.json) |

[→ View full connector details](../connectors/checkpointcyberintioc.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `iocsent_CL` | [Check Point Cyberint IOC Connector](../connectors/checkpointcyberintioc.md) |

[← Back to Solutions Index](../solutions-index.md)
