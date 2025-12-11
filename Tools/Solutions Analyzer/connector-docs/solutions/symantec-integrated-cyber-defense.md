# Symantec Integrated Cyber Defense

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Integrated%20Cyber%20Defense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Integrated%20Cyber%20Defense) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Symantec Integrated Cyber Defense Exchange](../connectors/symantec.md)

**Publisher:** Symantec

Symantec ICDx connector allows you to easily connect your Symantec security solutions logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect Symantec ICDx**

1. On the ICDx navigation bar, click **Configuration**.
2. At the top of the **Configuration** screen, click **Forwarders**, and next to Microsoft Sentinel (Log Analytics), click **Add**.
3. In the Microsoft Sentinel (Log Analytics) window that opens, click **Show Advanced**. [See the documentation to set advanced features](https://aka.ms/SymantecICDX-learn-more).
4. Make sure that you set a name for the forwarder and under Azure Destination, set these required fields:
  -   Workspace ID: Paste the Workspace ID from the Microsoft Sentinel portal connector page.
  -   Primary Key: Paste the Primary Key from the Microsoft Sentinel portal connector page.
  -   Custom Log Name: Type the custom log name in the Microsoft Azure portal Log Analytics workspace to which you are going to forward events. The default is SymantecICDx.
5. Click Save and to start the forwarder, go to Options > More and click **Start**.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `SymantecICDx_CL` |
| **Connector Definition Files** | [SymantecICDX.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Integrated%20Cyber%20Defense/Data%20Connectors/SymantecICDX.JSON) |

[→ View full connector details](../connectors/symantec.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SymantecICDx_CL` | [Symantec Integrated Cyber Defense Exchange](../connectors/symantec.md) |

[← Back to Solutions Index](../solutions-index.md)
