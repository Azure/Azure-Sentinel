# SpyCloud MDE Automation Playbook

This playbook automates endpoint response actions in Microsoft Defender for Endpoint (MDE) when SpyCloud breach data identifies compromised machines.

**Capabilities**
- Machine isolation in Defender for Endpoint
- Machine tagging for tracking, grouping, and policy targeting
- IOC submission to Defender Threat Intelligence
- Microsoft Sentinel incident creation
- Email notifications
- Execution log ingestion to `Spycloud_MDE_LogsV2_CL`

## Prerequisites

- App Registration with the Microsoft Graph and WindowsDefenderATP permissions listed in the [Integration Guide](../../SpyCloud_Sentinel_Integration_Guide.md), Section 2.1
- DCR Immutable ID and DCE Logs Ingestion Endpoint URL for `Spycloud_MDE_LogsV2_CL` (Section 2.2)
- Monitoring Metrics Publisher role assigned to the App Registration on that DCR

## Deployment

1. In the Azure Portal, navigate to **Deploy a custom template**
2. Select this template (`azuredeploy.json`)
3. Confirm Subscription, Resource Group, and Region
4. Enter a value for **PlaybookName** (this is the only ARM deployment-time parameter)
5. Click **Review + Create**, then **Create**
6. Authorize the `office365`, `WindowsDefenderATP`, and `azuresentinel` API connections created by the deployment

## Post-deployment configuration

All other settings are **workflow parameters**, baked into the Logic App with default values. After the playbook is deployed, update them with your own values:

1. Navigate to the Microsoft Sentinel workspace, open **Automation**, and select the `SpyCloud_MDE_Automation` playbook — or go directly to the Logic App resource in the Azure Portal
2. Open the Logic App and click **Edit** to open the workflow designer
3. Open the **Parameters** section (in the designer toolbar, or under **Development Tools → Workflow parameters**)
4. For each parameter listed below, enter the appropriate value for your environment
5. Click **Save** to apply the changes to the playbook

| Parameter | Type | Default | Description |
|---|---|---|---|
| Isolate_Machine | Bool | false | Enables automatic machine isolation in Defender for Endpoint |
| Machine_Tag_Value | String | (empty) | Tag value applied to affected machines |
| Save_IOCs_Defender | Bool | false | Enables submitting IOCs to Defender Threat Intelligence |
| IOC_Expiration_Days | Int | 30 | Days before a submitted IOC expires in Defender |
| Spycloud_Defender_DCE_Endpoint | String | (empty) | DCE Logs Ingestion Endpoint URL |
| Spycloud_Defender_DCE_Immutable_ID | String | (empty) | DCR Immutable ID for `Spycloud_MDE_LogsV2_CL` |
| TenantID | String | (empty) | Azure Tenant ID |
| ClientID | String | (empty) | App Registration Client ID |
| Client_Secret | String | (empty) | App Registration Client Secret |
| Ingestion_Table_Name | String | Spycloud_MDE_LogsV2_CL | Custom Log Analytics table for playbook logs |
| create_incident_in_sentinel | Bool | false | Enables automatic Sentinel incident creation |
| Workspace_Name | String | Your workspace name | Log Analytics Workspace name |
| Defender_IOC_Action_Type | String | Alert | IOC action in Defender, e.g. Alert, Warn, Block, Audit, or AlertAndBlock |
| notification_email | String | (empty) | Notification email address(es), semicolon-separated |

After saving workflow parameters, confirm `SpyCloud_MDE_Automation` shows status **Enabled** and check Run History for immediate failures.
