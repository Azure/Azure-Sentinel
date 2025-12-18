# Sevco Platform - Devices

| | |
|----------|-------|
| **Connector ID** | `SevcoDevices` |
| **Publisher** | Sevco Security |
| **Tables Ingested** | [`Sevco_Devices_CL`](../tables-index.md#sevco_devices_cl) |
| **Used in Solutions** | [SevcoSecurity](../solutions/sevcosecurity.md) |
| **Connector Definition Files** | [Connector_SevcoSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SevcoSecurity/Data%20Connectors/Connector_SevcoSecurity.json) |

The Sevco Platform - Devices connector allows you to easily connect your Sevco Device Assets with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s assets and improves your security operation capabilities.



[For more information >​](https://docs.sev.co/docs/microsoft-sentinel-inventory)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect to Sevco**

The Sevco Platform can integrate with and export assets directly to Microsoft Sentinel..​

1.  Go to [Sevco - Microsoft Sentinel Integration](https://docs.sev.co/docs/microsoft-sentinel-inventory), and follow the instructions, using the parameters below to set up the connection:.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
