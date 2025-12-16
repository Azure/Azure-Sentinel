# Varonis Purview

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Varonis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varonis.com/resources/support](https://www.varonis.com/resources/support) |
| **Categories** | domains |
| **First Published** | 2025-10-27 |
| **Last Updated** | 2025-10-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Varonis%20Purview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Varonis%20Purview) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Varonis Purview Push Connector](../connectors/varonispurviewpush.md)

**Publisher:** Varonis

The [Varonis Purview](https://www.varonis.com/) connector provides the capability to sync resources from Varonis to Microsoft Purview.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rule (DCR). Typically requires Azure RBAC Owner or User Access Administrator role

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Run this to setup ingestion for Varonis Resoources**

This will create the necessary Log Analytics tables, Data Collection Rule (DCR), and an Entra application to securely send data to the DCR.
#### Automated Configuration and Secure Data Ingestion with Entra Application 
Clicking on "Deploy" will trigger the creation of Log Analytics tables and a Data Collection Rule (DCR). 
It will then create an Entra application, link the DCR to it, and set the entered secret in the application. This setup enables data to be sent securely to the DCR using an Entra token.
Deploy Varonis connector resources

**2. Push your logs into the workspace**

Use the following parameters to configure the Varonis Purview Connector in your Varonis integrations dashboard.
- **Tenant ID (Directory ID)**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Application ID**: `ApplicationId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Secret**: `ApplicationSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Endpoint Uri**: `DataCollectionEndpoint`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Rule Immutable ID**: `DataCollectionRuleId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Resources Stream Name**: `Custom-varonisresources`

| | |
|--------------------------|---|
| **Tables Ingested** | `varonisresources_CL` |
| **Connector Definition Files** | [VaronisPurview_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Varonis%20Purview/Data%20Connectors/VaronisPurview_ccp/VaronisPurview_connectorDefinition.json) |

[→ View full connector details](../connectors/varonispurviewpush.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `varonisresources_CL` | [Varonis Purview Push Connector](../connectors/varonispurviewpush.md) |

[← Back to Solutions Index](../solutions-index.md)
