# BETTER Mobile Threat Defense (MTD)

| | |
|----------|-------|
| **Connector ID** | `BetterMTD` |
| **Publisher** | BETTER Mobile |
| **Tables Ingested** | [`BetterMTDAppLog_CL`](../tables-index.md#bettermtdapplog_cl), [`BetterMTDDeviceLog_CL`](../tables-index.md#bettermtddevicelog_cl), [`BetterMTDIncidentLog_CL`](../tables-index.md#bettermtdincidentlog_cl), [`BetterMTDNetflowLog_CL`](../tables-index.md#bettermtdnetflowlog_cl) |
| **Used in Solutions** | [BETTER Mobile Threat Defense (MTD)](../solutions/better-mobile-threat-defense-(mtd).md) |
| **Connector Definition Files** | [BETTERMTD.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29/Data%20Connectors/BETTERMTD.json) |

The BETTER MTD Connector allows Enterprises to connect their Better MTD instances with Microsoft Sentinel, to view their data in Dashboards, create custom alerts, use it to trigger playbooks and expands threat hunting capabilities. This gives users more insight into their organization's mobile devices and ability to quickly analyze current mobile security posture which improves their overall SecOps capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

1. In **Better MTD Console**, click on **Integration** on the side bar.
2. Select  **Others** tab.
3. Click the **ADD ACCOUNT** button and Select **Microsoft Sentinel** from the available integrations.
4. Create the Integration:
  - set `ACCOUNT NAME` to a descriptive name that identifies the integration then click **Next**
  - Enter your `WORKSPACE ID` and `PRIMARY KEY` from the fields below, click **Save**
  - Click **Done**
5.  Threat Policy setup (Which Incidents should be reported to `Microsoft Sentinel`):
  - In **Better MTD Console**, click on **Policies** on the side bar
  - Click on the **Edit** button of the Policy that you are using.
  - For each Incident types that you want to be logged go to **Send to Integrations** field and select **Sentinel**
6. For additional information, please refer to our [Documentation](https://mtd-docs.bmobi.net/integrations/how-to-setup-azure-sentinel-integration#mtd-integration-configuration).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
