# SpyCloud Session Revocation Playbook

This playbook revokes active Microsoft Entra sign-in sessions for users named in a SpyCloud identity access record exposure.

Identity access records cover session cookies, OAuth tokens and SSO credentials. That material grants account access **without a password**, so it survives a password reset and defeats single-factor controls. Revoking active sessions is the primary containment action, which is why this playbook does that and nothing else.

**Capabilities**
- Revokes all active sign-in sessions for affected users
- Adds an explanatory comment to the incident
- Execution log ingestion to `SpyCloud_ConditionalAccessLogsV2_CL`

The deployment also creates the Microsoft Sentinel automation rule that invokes this playbook, so no separate wiring step is needed.

## Prerequisites

- App Registration with Microsoft Graph permission to revoke sessions (`User.RevokeSessions.All`, or `User.ReadWrite.All`), granted admin consent
- DCR Immutable ID and DCE Logs Ingestion Endpoint URL — the same pair used by the other SpyCloud playbooks
- Monitoring Metrics Publisher role assigned to the App Registration on that DCR
- **Microsoft Sentinel Automation Contributor** granted to the **Azure Security Insights** service principal on the resource group you are deploying into

### Grant Automation Contributor first

This deployment creates an automation rule alongside the Logic App, and Sentinel refuses to create one unless it already has permission to run playbooks in the target resource group. Without it the deployment fails with `Missing required permissions for Microsoft Sentinel on the playbook resource`.

```bash
az role assignment create \
  --role "Microsoft Sentinel Automation Contributor" \
  --assignee 98785600-1bb7-4fb9-b9fa-19afe2c8a360 \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>
```

`98785600-1bb7-4fb9-b9fa-19afe2c8a360` is the fixed application ID for Azure Security Insights.

### Finding the DCR immutable ID and DCE endpoint

Sentinel creates the data collection rule as `Microsoft-Sentinel-SpyCloudwatchlist-DCR-<guid>`, not under the name in the solution template, and pairs it with an auto-generated `asi-<guid>` endpoint. Read both from the live connector:

```bash
SUB=<subscription-id>; RG=<resource-group>; WS=<workspace-name>
az rest --method get --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01-preview" --query "value[?properties.dcrConfig] | [0].properties.dcrConfig.{immutableId: dataCollectionRuleImmutableId, endpoint: dataCollectionEndpoint}"
```

Note that `DCE_Immutable_ID` takes the **DCR's** immutable ID despite its name.

## Deployment

All settings are supplied at deployment time.

1. In the Azure Portal, navigate to **Deploy a custom template**
2. Select this template (`azuredeploy.json`)
3. Confirm Subscription, Resource Group, and Region
4. Complete the parameters below
5. Click **Review + Create**, then **Create**

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| PlaybookName | String | SpyCloud_Session_Revocation | Name of the Logic App resource |
| Revoke_User_Sessions | String | false | Set to `true` to revoke sessions. With `false` the playbook runs, comments on the incident and logs, but takes no action |
| ClientID | String | — | App Registration Client ID |
| TenantID | String | — | Azure Tenant ID |
| ClientSecret | SecureString | — | App Registration Client Secret |
| DCE_Endpoint | String | — | DCE Logs Ingestion Endpoint URL |
| DCE_Immutable_ID | String | — | DCR Immutable ID |
| Custom_Table_Name | String | SpyCloud_ConditionalAccessLogsV2_CL | Log table, shared with the Conditional Access playbook |
| Sentinel_Workspace_Resource_Id | String | Solution workspace | Workspace the automation rule is created in. Pre-filled when deploying from Content Hub |
| AccessRecordIncidentTitle | String | SpyCloud identity access record exposure | Incident title the automation rule matches on |
| Automation_Rule_Order | Int | 3 | Execution order of the automation rule |

`Revoke_User_Sessions` is a **string** with allowed values `true` / `false`, not a boolean. Microsoft Sentinel's Content Hub playbook editor renders no input control at all for ARM `bool` parameters, which would leave the toggle stuck at its default. The editor also ignores the declared allowed values and shows a plain textbox — **type exactly `true` or `false`**. Anything else fails the deployment when the value is converted back to a boolean, which is deliberate.

### API connections

The deployment creates one connection, `azuresentinel`, which uses the playbook's system-assigned managed identity. There is **no Authorize button** and none is needed. Grant that managed identity the **Microsoft Sentinel Responder** role on the workspace, or the playbook cannot read incident entities or comment on incidents.

Session revocation itself goes through Microsoft Graph using the App Registration, not through a connector.

## Automation rule

The deployment creates **SpyCloud - Revoke sessions on identity access record exposure**, which runs this playbook when an incident is created whose title contains `AccessRecordIncidentTitle`.

The rule is created in the same deployment as the Logic App it invokes, so there is no deployment order to observe.

It matches on **incident title**, not the analytic rule's resource ID, because activating a rule from a Content Hub template generates a new GUID every time. The `AR_Access_Records_30` rule uses an alert display name of `SpyCloud identity access record exposure - {{AccountUpn}}`, so matching is deliberately `Contains` rather than an exact comparison — Microsoft Defender also appends its own text to incident titles.

Beyond the managed identity role, the Automation Contributor grant under Prerequisites is what lets the rule invoke the playbook.

## Behaviour

`AR_Access_Records_30` uses `AlertPerResult` deduplicated by identity, so each exposed user produces their own alert, incident and playbook run. That means one user per run, and the loop is serialised regardless — sessions are never revoked for the wrong account.

With `Revoke_User_Sessions` set to `false`, every step still runs and logs, so you can observe what would have happened before enabling it. That is the recommended way to introduce this playbook.

## Post-deployment

1. Confirm `SpyCloud_Session_Revocation` shows status **Enabled** — it deploys `Disabled`
2. Confirm the managed identity has Microsoft Sentinel Responder on the workspace
3. Confirm the automation rule appears under **Microsoft Sentinel → Automation** and is enabled
4. Check Run History for immediate failures

## Known limitations

**Do not run this playbook manually from an incident.** Manual runs do not populate `properties.Alerts` in the trigger payload, so the first loop receives `null` and the run fails before any action. Use **Resubmit** on an earlier automation-triggered run instead.

**Users who do not exist in your tenant produce a failed Graph call.** Breach data frequently contains personal addresses and third-party accounts that have no Entra identity. The revocation call returns 404 for those and the run reports a failure — expected, not a fault.

**`BreachTitle` is always empty** in the log rows. It is not among the Custom Details the analytic rule emits; the column is retained for schema compatibility with the Conditional Access playbook.
