# SevcoSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-05-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SevcoSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SevcoSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Sevco Platform - Devices](../connectors/sevcodevices.md)

**Publisher:** Sevco Security

The Sevco Platform - Devices connector allows you to easily connect your Sevco Device Assets with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s assets and improves your security operation capabilities.



[For more information >​](https://docs.sev.co/docs/microsoft-sentinel-inventory)

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect to Sevco**

The Sevco Platform can integrate with and export assets directly to Microsoft Sentinel..​

1.  Go to [Sevco - Microsoft Sentinel Integration](https://docs.sev.co/docs/microsoft-sentinel-inventory), and follow the instructions, using the parameters below to set up the connection:.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `Sevco_Devices_CL` |
| **Connector Definition Files** | [Connector_SevcoSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SevcoSecurity/Data%20Connectors/Connector_SevcoSecurity.json) |

[→ View full connector details](../connectors/sevcodevices.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Sevco_Devices_CL` | [Sevco Platform - Devices](../connectors/sevcodevices.md) |

[← Back to Solutions Index](../solutions-index.md)
