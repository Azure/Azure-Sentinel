# SpyCloud MDE Automation Playbook

This playbook automates endpoint response actions in Microsoft Defender for Endpoint (MDE) when SpyCloud breach data identifies compromised machines.

**Capabilities**
- Machine isolation in Defender for Endpoint
- Machine tagging for tracking, grouping, and policy targeting
- IOC submission to Defender Threat Intelligence
- Optional Microsoft Sentinel incident creation
- Email notifications
- Execution log ingestion to `Spycloud_MDE_LogsV2_CL`

The deployment also creates the Microsoft Sentinel automation rule that invokes this playbook, so no separate wiring step is needed. See [Automation rule](#automation-rule) below.

## Prerequisites

- App Registration with the Microsoft Graph and WindowsDefenderATP permissions listed in the SpyCloud Sentinel Integration Guide, Section 2.1
- DCR Immutable ID and DCE Logs Ingestion Endpoint URL for `Spycloud_MDE_LogsV2_CL` (Section 2.2)
- Monitoring Metrics Publisher role assigned to the App Registration on that DCR
- **Microsoft Sentinel Automation Contributor** granted to the **Azure Security Insights** service principal on the resource group you are deploying into — see below

### Finding the DCR immutable ID and DCE endpoint

The solution template names its data collection rule `SpyCloudwatchlist-DCR`, but Microsoft Sentinel does not create it under that name. When you connect the data connector, Sentinel provisions the rule itself as `Microsoft-Sentinel-SpyCloudwatchlist-DCR-<guid>` and pairs it with an auto-generated `asi-<guid>` data collection endpoint. Searching for `SpyCloudwatchlist-DCR` in the portal will not find it, and if the connector has been connected more than once there will be several, only the most recent of which is in use.

Read both values from the live connector rather than hunting through the resource list:

```bash
SUB=<subscription-id>; RG=<resource-group>; WS=<workspace-name>
az rest --method get --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01-preview" --query "value[?properties.dcrConfig] | [0].properties.dcrConfig.{immutableId: dataCollectionRuleImmutableId, endpoint: dataCollectionEndpoint}"
```

All four pollers share the same rule and endpoint, so any one of them gives the right answer. Note that the endpoint you need is the **Logs Ingestion** URL — `...ingest.monitor.azure.com`, not the `...handler.control.monitor.azure.com` configuration-access URL shown alongside it on the DCE resource. Grant the App Registration **Monitoring Metrics Publisher** on that same rule.

### Grant Automation Contributor first

This deployment creates a Microsoft Sentinel automation rule alongside the Logic App, and Sentinel refuses to create an automation rule unless it already has permission to run playbooks in the target resource group. Without it the deployment fails with:

```
Missing required permissions for Microsoft Sentinel on the playbook resource '.../SpyCloud_MDE_Automation'
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
6. Authorize the `office365` and `WindowsDefenderATP` API connections created by the deployment

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| PlaybookName | String | SpyCloud_MDE_Automation | Name of the Logic App resource |
| Workspace_Name | String | — | Name of the Log Analytics workspace where Microsoft Sentinel is enabled. Used to build the incident path for the optional 'Create incident in Sentinel' action |
| Isolate_Machine | String | false | Enable automatic machine isolation in Defender for Endpoint |
| Machine_Tag_Value | String | — | Tag applied to affected machines in Defender for Endpoint. Leave blank to skip tagging |
| Save_IOCs_Defender | String | false | Submit breach-derived indicators to Defender Threat Intelligence |
| IOC_Expiration_Days | Int | 30 | Days before a submitted IOC expires in Defender |
| Spycloud_Defender_DCE_Endpoint | String | — | DCE Logs Ingestion Endpoint URL for MDE logs |
| Spycloud_Defender_DCE_Immutable_ID | String | — | DCR Immutable ID for `Spycloud_MDE_LogsV2_CL` |
| TenantID | String | — | Azure Tenant ID |
| ClientID | String | — | App Registration Client ID |
| Client_Secret | SecureString | — | App Registration Client Secret |
| Ingestion_Table_Name | String | Spycloud_MDE_LogsV2_CL | Custom Log Analytics table for playbook logs |
| create_incident_in_sentinel | String | false | Create a Microsoft Sentinel incident from the playbook |
| Defender_IOC_Action_Type | String | Alert | IOC action in Defender: Alert, Warn, Block, Audit, AlertAndBlock, BlockAndRemediate or Allowed |
| notification_email | String | — | Email address(es) for notifications, semicolon-separated |
| Sentinel_Workspace_Resource_Id | String | Solution workspace | Full resource ID of the Sentinel workspace the automation rule is created in. Pre-filled when deploying from Content Hub |
| MalwareIncidentTitle | String | SpyCloud infostealer malware credential exposure | Incident title the automation rule matches on |
| Automation_Rule_Order | Int | 1 | Execution order of the automation rule (lower runs first) |

Parameters typed **String** with values `true` / `false` are deliberate. Microsoft Sentinel's Content Hub playbook editor renders no input control at all for ARM `bool` parameters, which left every toggle stuck at its default and unusable from the gallery. As strings they are settable, but note the editor also ignores the declared allowed values and shows a plain textbox — **type exactly `true` or `false`**. Anything else fails the deployment when the value is converted back to a boolean, which is deliberate: a loud failure beats silently deploying with the action disabled.

Parameters shown with `—` have no default and must be supplied, including ones you may not intend to use.

### API connections

The deployment creates three API connections:

- **`office365`** — requires interactive authorization. Open the connection resource and click **Authorize**, then sign in with the account that will send notification emails.
- **`WindowsDefenderATP`** — requires interactive authorization. Open the connection resource and click **Authorize**, then sign in with the account that will perform MDE actions.
- **`azuresentinel`** — uses the playbook's system-assigned managed identity. There is **no Authorize button** and none is needed. Instead, grant the playbook's managed identity the **Microsoft Sentinel Responder** role on the workspace, or the playbook cannot read incident entities or create incidents.

## Automation rule

The deployment creates the automation rule **SpyCloud - Isolate compromised device on malware exposure**, which runs this playbook whenever an incident is created whose title contains the value of `MalwareIncidentTitle`.

The rule is created in the same deployment as the Logic App it invokes, so there is no deployment order to observe and no risk of it referencing a playbook that does not exist.

It matches on **incident title**, not on the analytic rule's resource ID. Microsoft Sentinel sets the incident title from the analytic rule's display name, and activating a rule from a Content Hub template generates a new GUID every time — so a rule ID baked into this template could never match a customer's deployed rule and the automation would silently never fire. If you rename the analytic rule when creating it, set `MalwareIncidentTitle` to match.

The analytic rule does not need to exist before this deployment; incident titles are not validated against anything. Activating it last is preferable, so the first incident it raises already has remediation wired up.

The **Microsoft Sentinel Automation Contributor** assignment covered under Prerequisites is what allows this rule to be created at all, and what lets it invoke the playbook once deployed.

## Post-deployment

1. Confirm `SpyCloud_MDE_Automation` shows status **Enabled**
2. Confirm the managed identity role assignment above is in place
3. Confirm the automation rule appears under **Microsoft Sentinel → Automation** and is enabled
4. Check Run History for immediate failures

## Known limitations

**Do not run this playbook manually from an incident.** Manual runs do not populate `properties.Alerts` in the trigger payload, so the playbook's first loop receives `null` and the run fails at `For each incident alert` before any remediation occurs. The playbook is designed to be invoked by its automation rule. To re-run against a previous incident, use **Resubmit** on an earlier automation-triggered run instead.

**The remediation log records successes only.** Rows are written to `Spycloud_MDE_LogsV2_CL` only for machines that resolve in Defender for Endpoint and complete their action branch — a machine that returns 404 from Defender produces no row. If IOC submission fails, the host loop does not run at all and no rows are written for any machine. Treat that table as a record of completed actions, not a complete audit of everything the playbook considered.
