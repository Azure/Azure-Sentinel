# F5 BIG-IP

| | |
|----------|-------|
| **Connector ID** | `F5BigIp` |
| **Publisher** | F5 Networks |
| **Tables Ingested** | [`F5Telemetry_ASM_CL`](../tables-index.md#f5telemetry_asm_cl), [`F5Telemetry_LTM_CL`](../tables-index.md#f5telemetry_ltm_cl), [`F5Telemetry_system_CL`](../tables-index.md#f5telemetry_system_cl) |
| **Used in Solutions** | [F5 BIG-IP](../solutions/f5-big-ip.md) |
| **Connector Definition Files** | [F5BigIp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP/Data%20Connectors/F5BigIp.json) |

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect F5 BIGIP**

To connect your F5 BIGIP, you have to post a JSON declaration to the system’s API endpoint. For instructions on how to do this, see [Integrating the F5 BGIP with Microsoft Sentinel](https://aka.ms/F5BigIp-Integrate).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
