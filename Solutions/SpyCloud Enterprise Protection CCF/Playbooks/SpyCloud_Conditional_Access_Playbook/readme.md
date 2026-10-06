# SpyCloud Conditional Access Playbook

This playbook automates Azure AD / Entra ID identity response actions when SpyCloud breach data identifies compromised user credentials.

**Capabilities**
- Account disablement
- Session revocation across all applications
- Forced password reset at next sign-in
- Conditional Access group membership enforcement
- Email notifications
- Execution log ingestion to `SpyCloud_ConditionalAccessLogsV2_CL`

The deployment also creates the Microsoft Sentinel automation rule that invokes this playbook, so no separate wiring step is needed. See [Automation rule](#automation-rule) below.

## Prerequisites

- App Registration with the Microsoft Graph permissions listed in the SpyCloud Sentinel Integration Guide, Section 2.1
- DCR Immutable ID and DCE Logs Ingestion Endpoint URL for `SpyCloud_ConditionalAccessLogsV2_CL` (Section 2.2)
- Monitoring Metrics Publisher role assigned to the App Registration on that DCR
- Object ID of the Azure AD Conditional Access enforcement group (if using group membership actions)
- **Microsoft Sentinel Automation Contributor** granted to the **Azure Security Insights** service principal on the resource group you are deploying into — see below

### Finding the DCR immutable ID and DCE endpoint

The solution template names its data collection rule `SpyCloudwatchlist-DCR`, but Microsoft Sentinel does not create it under that name. When you connect the data connector, Sentinel provisions the rule itself as `Microsoft-Sentinel-SpyCloudwatchlist-DCR-<guid>` and pairs it with an auto-generated `asi-<guid>` data collection endpoint. Searching for `SpyCloudwatchlist-DCR` in the portal will not find it, and if the connector has been connected more than once there will be several, only the most recent of which is in use.

Read both values from the live connector rather than hunting through the resource list:

```bash
SUB=<subscription-id>; RG=<resource-group>; WS=<workspace-name>
az rest --method get --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01-preview" --query "value[?properties.dcrConfig] | [0].properties.dcrConfig.{immutableId: dataCollectionRuleImmutableId, endpoint: dataCollectionEndpoint}"
```

All four pollers share the same rule and endpoint, so any one of them gives the right answer. Grant the App Registration **Monitoring Metrics Publisher** on that same rule.

### Grant Automation Contributor first

This deployment creates a Microsoft Sentinel automation rule alongside the Logic App, and Sentinel refuses to create an automation rule unless it already has permission to run playbooks in the target resource group. Without it the deployment fails with:

```
Missing required permissions for Microsoft Sentinel on the playbook resource '.../SpyCloud_Conditional_Access_Playbook'
```

Grant it once per resource group, before deploying either playbook:

```bash
az role assignment create \
  --role "Microsoft Sentinel Automation Contributor" \
  --assignee 98785600-1bb7-4fb9-b9fa-19afe2c8a360 \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>
```

`98785600-1bb7-4fb9-b9fa-19afe2c8a360` is the fixed application ID for Azure Security Insights. In the portal, use **Access control (IAM)** on the resource group → **Add role assignment** → *Microsoft Sentinel Automation Contributor* → search for **Azure Security Insights**.

This permission has always been required for the automation to work. It is now enforced at deployment time rather than allowing a rule to be created that silently never fires.

## Deployment

All settings are supplied at deployment time. There is no post-deployment parameter editing.

1. In the Azure Portal, navigate to **Deploy a custom template**
2. Select this template (`azuredeploy.json`)
3. Confirm Subscription, Resource Group, and Region
4. Complete the parameters below
5. Click **Review + Create**, then **Create**
6. Authorize the `office365` API connection created by the deployment

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| PlaybookName | String | SpyCloud_Conditional_Access_Playbook | Name of the Logic App resource |
| Notify_Users_Emails | String | — | Email address(es) for notifications, semicolon-separated |
| Force_Password_Reset_On_Next_SignIn | String | false | Forces password reset at next sign-in for affected users |
| Disable_User | String | false | Disables affected Entra ID user accounts |
| Add_User_To_Azure_CA_Group | String | false | Adds affected users to the Conditional Access enforcement group |
| Azure_CA_Group_Object_ID | String | — | Object ID of the Entra ID Conditional Access group |
| Revoke_User_Sessions | String | false | Revokes all active sign-in sessions for affected users |
| ClientID | String | — | App Registration Client ID |
| TenantID | String | — | Azure Tenant ID |
| ClientSecret | SecureString | — | App Registration Client Secret |
| DCE_Endpoint | String | — | DCE Logs Ingestion Endpoint URL for CA logs |
| DCE_Immutable_ID | String | — | DCR Immutable ID for `SpyCloud_ConditionalAccessLogsV2_CL` |
| Custom_Table_Name | String | SpyCloud_ConditionalAccessLogsV2_CL | Custom Log Analytics table for playbook logs |
| Sentinel_Workspace_Resource_Id | String | Solution workspace | Full resource ID of the Sentinel workspace the automation rule is created in. Pre-filled when deploying from Content Hub |
| BreachedUsersIncidentTitle | String | SpyCloud plaintext credential exposure detected | Incident title the automation rule matches on |
| Automation_Rule_Order | Int | 2 | Execution order of the automation rule (lower runs first) |

Parameters typed **String** with values `true` / `false` are deliberate. Microsoft Sentinel's Content Hub playbook editor renders no input control at all for ARM `bool` parameters, which left every toggle stuck at its default and unusable from the gallery. As strings they are settable, but note the editor also ignores the declared allowed values and shows a plain textbox — **type exactly `true` or `false`**. Anything else fails the deployment when the value is converted back to a boolean, which is deliberate: a loud failure beats silently deploying with the action disabled.

Parameters shown with `—` have no default and must be supplied, including ones you may not intend to use. If you are not using Conditional Access group enforcement, leave `Add_User_To_Azure_CA_Group` set to `false` and enter any placeholder text for `Azure_CA_Group_Object_ID`; it is not read unless the toggle is enabled.

### API connections

The deployment creates two API connections:

- **`office365`** — requires interactive authorization. Open the connection resource and click **Authorize**, then sign in with the account that will send notification emails.
- **`azuresentinel`** — uses the playbook's system-assigned managed identity. There is **no Authorize button** and none is needed. Instead, grant the playbook's managed identity the **Microsoft Sentinel Responder** role on the workspace, or the playbook cannot read incident entities.

## Automation rule

The deployment creates the automation rule **SpyCloud - Enforce Conditional Access on credential exposure**, which runs this playbook whenever an incident is created whose title contains the value of `BreachedUsersIncidentTitle`.

The rule is created in the same deployment as the Logic App it invokes, so there is no deployment order to observe and no risk of it referencing a playbook that does not exist.

It matches on **incident title**, not on the analytic rule's resource ID. Microsoft Sentinel sets the incident title from the analytic rule's display name, and activating a rule from a Content Hub template generates a new GUID every time — so a rule ID baked into this template could never match a customer's deployed rule and the automation would silently never fire. If you rename the analytic rule when creating it, set `BreachedUsersIncidentTitle` to match.

The analytic rules do **not** need to exist before this deployment; incident titles are not validated against anything. Activating them last is preferable, so the first incident they raise already has remediation wired up.

There is no automation rule for `AR_Access_Records_30` (identity access record exposure). That rule raises incidents for triage but has no automated response playbook.

The **Microsoft Sentinel Automation Contributor** assignment covered under Prerequisites is what allows this rule to be created at all, and what lets it invoke the playbook once deployed.

## Post-deployment

1. Confirm `SpyCloud_Conditional_Access_Playbook` shows status **Enabled**
2. Confirm the managed identity role assignment above is in place
3. Confirm the automation rule appears under **Microsoft Sentinel → Automation** and is enabled
4. Check Run History for immediate failures

## Known limitations

**Do not run this playbook manually from an incident.** Manual runs do not populate `properties.Alerts` in the trigger payload, so the playbook's first loop receives `null` and the run fails at `For each incident alert` before any remediation occurs. The playbook is designed to be invoked by its automation rule. To re-run against a previous incident, use **Resubmit** on an earlier automation-triggered run instead.

**The remediation log records successes only.** `Log_ingestion` runs inside the user-enabled condition branch, which is reached only after the Microsoft Graph user lookup succeeds. Users who cannot be resolved in your tenant — deleted accounts, external identities, or the personal email addresses that commonly appear in breach data — produce no row in `SpyCloud_ConditionalAccessLogsV2_CL`. Treat that table as a record of completed actions, not a complete audit of everyone the playbook considered.
