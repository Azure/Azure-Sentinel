# Cyble Vision

## Solution Information

| | |
|------------------------|-------|
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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Cyble Vision API token**: An API Token from Cyble Vision Platform is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Step 1 - Generating API Token from Cyble Platform**

Navigate to [Cyble Platform](https://cyble.ai/utilities/access-apis) and log in using your Cyble Vision credentials.

Once logged in, go to the left-hand panel and scroll down to **Utilities**. Click on **Access APIs**. On the top-right corner of the page, click the **+ (Add)** icon to generate a new API key. Provide an alias (a friendly name for your key) and click **Generate**. Copy the generated API token and store it securely.

**2. STEP 2 - Configure the Data Connector**

Return to Microsoft Sentinel and open the **Cyble Vision Alerts** data connector configuration page. Paste your Cyble API Token into the **API Token** field under 'API Details'.
- **API Token**: (password field)
- **Query Interval (in minutes)**: Enter Time in Minutes (e.g., 10)
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `CybleVisionAlerts_CL` |
| **Connector Definition Files** | [CybleVisionAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Data%20Connectors/CybleVisionAlerts_CCF/CybleVisionAlerts_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyblevisionalerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CybleVisionAlerts_CL` | [Cyble Vision Alerts](../connectors/cyblevisionalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
