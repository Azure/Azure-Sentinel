# DruvaDataSecurityCloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Druva Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://support.druva.com/](https://support.druva.com/) |
| **Categories** | domains |
| **First Published** | 2024-12-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Druva Events Connector](../connectors/druvaeventccpdefinition.md)

**Publisher:** Microsoft

Provides capability to ingest the Druva events from Druva APIs

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permission are required

**Custom Permissions:**
- **Druva API Access**: Druva API requires a client id and client secret to authenticate

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>Note: Configurations to connect to Druva Rest API

Step 1: Create credentials from Druva console. Refer this doc for steps:- https://help.druva.com/en/articles/8580838-create-and-manage-api-credentials

Step 2: Enter the hostname. For public cloud its apis.druva.com

Step 3: Enter client id and client secret key

**4. Connect to Druva API to start collecting logs in Microsoft Sentinel**

Provide required values:
- **Hostname**: Example: apis.druva.com
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate

| | |
|--------------------------|---|
| **Tables Ingested** | `DruvaInsyncEvents_CL` |
| | `DruvaPlatformEvents_CL` |
| | `DruvaSecurityEvents_CL` |
| **Connector Definition Files** | [Druva_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Data%20Connectors/Druva_ccp/Druva_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/druvaeventccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DruvaInsyncEvents_CL` | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) |
| `DruvaPlatformEvents_CL` | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) |
| `DruvaSecurityEvents_CL` | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
