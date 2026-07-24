# SpyCloud Conditional Access Playbook

This playbook automates Azure AD / Entra ID identity response actions when SpyCloud breach data identifies compromised user credentials.

**Capabilities**
- Account disablement
- Session revocation across all applications
- Forced password reset at next sign-in
- Conditional Access group membership enforcement
- Email notifications
- Execution log ingestion to `SpyCloud_ConditionalAccessLogsV2_CL`

## Prerequisites

- App Registration with the Microsoft Graph permissions listed in the [Integration Guide](../../SpyCloud_Sentinel_Integration_Guide.md), Section 2.1
- DCR Immutable ID and DCE Logs Ingestion Endpoint URL for `SpyCloud_ConditionalAccessLogsV2_CL` (Section 2.2)
- Monitoring Metrics Publisher role assigned to the App Registration on that DCR
- Object ID of the Azure AD Conditional Access enforcement group (if using group membership actions)

## Deployment

1. In the Azure Portal, navigate to **Deploy a custom template**
2. Select this template (`azuredeploy.json`)
3. Confirm Subscription, Resource Group, and Region
4. Enter a value for **PlaybookName** (this is the only ARM deployment-time parameter)
5. Click **Review + Create**, then **Create**
6. Authorize the `office365` and `azuresentinel` API connections created by the deployment

## Post-deployment configuration

All other settings are **workflow parameters**, baked into the Logic App with default values. After the playbook is deployed, update them with your own values:

1. Navigate to the Microsoft Sentinel workspace, open **Automation**, and select the `SpyCloud_Conditional_Access_Playbook` playbook — or go directly to the Logic App resource in the Azure Portal
2. Open the Logic App and click **Edit** to open the workflow designer
3. Open the **Parameters** section (in the designer toolbar, or under **Development Tools → Workflow parameters**)
4. For each parameter listed below, enter the appropriate value for your environment
5. Click **Save** to apply the changes to the playbook

| Parameter | Type | Default | Description |
|---|---|---|---|
| Notify_Users_Emails | String | (empty) | Email address(es) for notifications, semicolon-separated |
| Force_Password_Reset_On_Next_SignIn | Bool | false | Forces password reset at next sign-in for affected users |
| Disable_User | Bool | false | Disables affected Azure AD user accounts |
| Add_User_To_Azure_CA_Group | Bool | false | Adds affected users to the Conditional Access enforcement group |
| Azure_CA_Group_Object_ID | String | (empty) | Object ID of the Azure AD Conditional Access group |
| Revoke_User_Sessions | Bool | false | Revokes all active sign-in sessions for affected users |
| ClientID | String | (empty) | App Registration Client ID |
| TenantID | String | (empty) | Azure Tenant ID |
| ClientSecret | String | (empty) | App Registration Client Secret |
| DCE_Endpoint | String | (empty) | DCE Logs Ingestion Endpoint URL for CA logs |
| DCE_Immutable_ID | String | (empty) | DCR Immutable ID for `SpyCloud_ConditionalAccessLogsV2_CL` |
| Custom_Table_Name | String | SpyCloud_ConditionalAccessLogsV2_CL | Custom Log Analytics table for playbook logs |

After saving workflow parameters, confirm `SpyCloud_Conditional_Access_Playbook` shows status **Enabled** and check Run History for immediate failures.
