# ForescoutHostPropertyMonitor

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Forescout Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forescout.com/support](https://www.forescout.com/support) |
| **Categories** | domains |
| **First Published** | 2022-06-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md)

**Publisher:** Forescout

The Forescout Host Property Monitor connector allows you to connect host/policy/compliance properties from Forescout platform with Microsoft Sentinel, to view, create custom incidents, and improve investigation. This gives you more insight into your organization network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Forescout Plugin requirement**: Please make sure Forescout Microsoft Sentinel plugin is running on Forescout platform

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Instructions on how to configure Forescout Microsoft Sentinel plugin are provided at Forescout Documentation Portal (https://docs.forescout.com/bundle/microsoft-sentinel-module-v2-0-0-h)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `ForescoutComplianceStatus_CL` |
| | `ForescoutHostProperties_CL` |
| | `ForescoutPolicyStatus_CL` |
| **Connector Definition Files** | [ForescoutHostPropertyMonitor.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor/Data%20Connectors/ForescoutHostPropertyMonitor.json) |

[→ View full connector details](../connectors/forescouthostpropertymonitor.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ForescoutComplianceStatus_CL` | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) |
| `ForescoutHostProperties_CL` | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) |
| `ForescoutPolicyStatus_CL` | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) |

[← Back to Solutions Index](../solutions-index.md)
