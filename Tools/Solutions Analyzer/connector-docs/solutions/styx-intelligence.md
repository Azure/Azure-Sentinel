# Styx Intelligence

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Styx Intelligence |
| **Support Tier** | Partner |
| **Support Link** | [https://www.styxintel.com/contact-us/](https://www.styxintel.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-02-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Styx%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Styx%20Intelligence) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [StyxView Alerts (via Codeless Connector Platform)](../connectors/styxviewendpointconnectordefinition.md)

**Publisher:** Styx Intelligence

The [StyxView Alerts](https://styxintel.com/) data connector enables seamless integration between the StyxView Alerts platform and Microsoft Sentinel. This connector ingests alert data from the StyxView Alerts API, allowing organizations to centralize and correlate actionable threat intelligence directly within their Microsoft Sentinel workspace.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **StyxView Alert API access**: Access to the StyxView Alerts API through an API key is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to StyxView Alerts API to start collecting alert logs in Microsoft Sentinel**

Contact Styx Intelligence Support (support.team@styxintel.com) to get access to an API key.
- **API Token**: (password field)
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `StyxViewAlerts_CL` |
| **Connector Definition Files** | [StyxView%20Alerts_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Styx%20Intelligence/Data%20Connectors/Alerts/StyxView%20Alerts_ConnectorDefinition.json) |

[→ View full connector details](../connectors/styxviewendpointconnectordefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `StyxViewAlerts_CL` | [StyxView Alerts (via Codeless Connector Platform)](../connectors/styxviewendpointconnectordefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
