# Onapsis Defend

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Onapsis |
| **Support Tier** | Partner |
| **Support Link** | [https://onapsis.com/support/](https://onapsis.com/support/) |
| **Categories** | domains |
| **First Published** | 2025-07-17 |
| **Last Updated** | 2025-07-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Defend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Defend) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Onapsis Defend Integration](../connectors/onapsis.md)

**Publisher:** Onapsis Platform

Onapsis Defend Integration is aimed at forwarding alerts and logs collected and detected by Onapsis Platform into Microsoft Sentinel SIEM

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required.

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rules. Typically requires Azure RBAC Owner or User Access Administrator role.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provide the Required Permissions**

We will create data collection rule (DCR) and data collection endpoint (DCE) resources. We will also create a Microsoft Entra app registration and assign the required permissions to it.
#### Automated deployment of Azure resources
Clicking on "Deploy push connector resources" will trigger the creation of DCR and DCE resources.
It will then create a Microsoft Entra app registration with client secret and grant permissions on the DCR. This setup enables data to be sent securely to the DCR using a OAuth v2 client credentials.
- Deploy push connector resources
  Application: Onapsis Defend Integration push to Microsoft Sentinel

**2. Maintain the data collection endpoint details and authentication info in Onapsis Defend Integration**

Share the data collection endpoint URL and authentication info with the Onapsis Defend Integration administrator to configure the Onapsis Defend Integration to send data to the data collection endpoint.
- **Use this value to configure as Tenant ID in the LogIngestionAPI credential.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra Application ID**: `ApplicationId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra Application Secret**: `ApplicationSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Use this value to configure the LogsIngestionURL parameter when deploying the IFlow.**: `DataCollectionEndpoint`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **DCR Immutable ID**: `DataCollectionRuleId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `Onapsis_Defend_CL` |
| **Connector Definition Files** | [Onapsis.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Defend/Data%20Connectors/Onapsis.json) |

[→ View full connector details](../connectors/onapsis.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Onapsis_Defend_CL` | [Onapsis Defend Integration](../connectors/onapsis.md), [Onapsis Defend: Integrate Unmatched SAP Threat Detection & Intel with Microsoft Sentinel](../connectors/onapsis.md) |

[← Back to Solutions Index](../solutions-index.md)
