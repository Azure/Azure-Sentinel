# Forescout eyeInspect for OT Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Forescout Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forescout.com/support](https://www.forescout.com/support) |
| **Categories** | domains |
| **First Published** | 2025-07-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forescout eyeInspect for OT Security](../connectors/forescout-eyeinspect-for-ot-security.md)

**Publisher:** Forescout

Forescout eyeInspect for OT Security connector allows you to connect Asset/Alert information from Forescout eyeInspect OT platform with Microsoft Sentinel, to view and analyze data using Log Analytics Tables and Workbooks. This gives you more insight into OT organization network and improves security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Forescout eyeInspect OT Microsoft Sentinel Integration**

Instructions on how to configure Forescout eyeInspect Microsoft Sentinel Integration are provided at Forescout eyeInspect Documentation Portal
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `ForescoutOtAlert_CL` |
| | `ForescoutOtAsset_CL` |
| **Connector Definition Files** | [Forescout%20eyeInspect%20for%20OT%20Security.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security/Data%20Connectors/Forescout%20eyeInspect%20for%20OT%20Security.json) |

[→ View full connector details](../connectors/forescout-eyeinspect-for-ot-security.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ForescoutOtAlert_CL` | [Forescout eyeInspect for OT Security](../connectors/forescout-eyeinspect-for-ot-security.md) |
| `ForescoutOtAsset_CL` | [Forescout eyeInspect for OT Security](../connectors/forescout-eyeinspect-for-ot-security.md) |

[← Back to Solutions Index](../solutions-index.md)
