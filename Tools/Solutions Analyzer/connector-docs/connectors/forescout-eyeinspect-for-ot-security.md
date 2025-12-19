# Forescout eyeInspect for OT Security

| | |
|----------|-------|
| **Connector ID** | `Forescout_eyeInspect_for_OT_Security` |
| **Publisher** | Forescout |
| **Tables Ingested** | [`ForescoutOtAlert_CL`](../tables-index.md#forescoutotalert_cl), [`ForescoutOtAsset_CL`](../tables-index.md#forescoutotasset_cl) |
| **Used in Solutions** | [Forescout eyeInspect for OT Security](../solutions/forescout-eyeinspect-for-ot-security.md) |
| **Connector Definition Files** | [Forescout%20eyeInspect%20for%20OT%20Security.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security/Data%20Connectors/Forescout%20eyeInspect%20for%20OT%20Security.json) |

Forescout eyeInspect for OT Security connector allows you to connect Asset/Alert information from Forescout eyeInspect OT platform with Microsoft Sentinel, to view and analyze data using Log Analytics Tables and Workbooks. This gives you more insight into OT organization network and improves security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Forescout eyeInspect OT Microsoft Sentinel Integration**

Instructions on how to configure Forescout eyeInspect Microsoft Sentinel Integration are provided at Forescout eyeInspect Documentation Portal
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
