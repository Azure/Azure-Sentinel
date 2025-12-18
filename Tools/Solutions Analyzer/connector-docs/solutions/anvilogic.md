# Anvilogic

## Solution Information

| | |
|------------------------|-------|
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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Anvilogic Application Registration Client ID and Client Secret**: To access the Anvilogic ADX we require the client id and client secret from the Anvilogic app registration

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Anvilogic to start collecting events of interest in Microsoft Sentinel**

Complete the form to ingest Anvilogic Alerts into your Microsoft Sentinel
- **Token Endpoint**: https://login[.]microsoftonline[.]com/<tenant_id>/oauth2/v2.0/token
- **Anvilogic ADX Scope**: <avl_adx_uri>/.default
- **Anvilogic ADX Request URI**: <avl_adx_uri>/v2/rest/query
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate

| | |
|--------------------------|---|
| **Tables Ingested** | `Anvilogic_Alerts_CL` |
| **Connector Definition Files** | [Anvilogic_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Anvilogic/Data%20Connectors/AnviLogic_CCF/Anvilogic_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/anvilogicccfdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Anvilogic_Alerts_CL` | [Anvilogic](../connectors/anvilogicccfdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
