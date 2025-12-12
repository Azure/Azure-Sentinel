# Beyond Security beSECURE

| | |
|----------|-------|
| **Connector ID** | `BeyondSecuritybeSECURE` |
| **Publisher** | Beyond Security |
| **Tables Ingested** | [`beSECURE_Audit_CL`](../tables-index.md#besecure_audit_cl), [`beSECURE_ScanEvent_CL`](../tables-index.md#besecure_scanevent_cl), [`beSECURE_ScanResults_CL`](../tables-index.md#besecure_scanresults_cl) |
| **Used in Solutions** | [Beyond Security beSECURE](../solutions/beyond-security-besecure.md) |
| **Connector Definition Files** | [Beyond%20Security%20beSECURE.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Beyond%20Security%20beSECURE/Data%20Connectors/Beyond%20Security%20beSECURE.json) |

The [Beyond Security beSECURE](https://beyondsecurity.com/) connector allows you to easily connect your Beyond Security beSECURE scan events, scan results and audit trail with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure beSECURE**

Follow the steps below to configure your beSECURE solution to send out scan results, scan status and audit trail to Azure Sentinel.
**1. Access the Integration menu**

  1.1 Click on the 'More' menu option

1.2 Select Server

1.3 Select Integration

1.4 Enable Azure Sentinel

  **2. Provide Azure Sentinel settings**

  Fill in the Workspace ID and Primary Key values, click 'Modify'
  - **Workspace ID**: `WorkspaceId`
    > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
  - **Primary Key**: `PrimaryKey`
    > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
