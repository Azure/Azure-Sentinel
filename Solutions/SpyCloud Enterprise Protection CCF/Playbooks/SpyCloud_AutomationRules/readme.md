# SpyCloud Automation Rules

This template deploys two Microsoft Sentinel automation rules that connect the SpyCloud analytic rules to the SpyCloud response playbooks, so incidents are automatically routed to the right automation without manual configuration.

| Automation Rule | Triggers On | Runs Playbook |
|---|---|---|
| SpyCloud - Isolate compromised device on malware exposure | Incident created from **AR_malware_25** (SpyCloud infostealer malware credential exposure) | `SpyCloud_MDE_Automation` |
| SpyCloud - Enforce Conditional Access on credential exposure | Incident created from **AR_Breached_Users_20** (SpyCloud plaintext credential exposure detected) | `SpyCloud_Conditional_Access_Playbook` |

## Prerequisites

- The `SpyCloud_MDE_Automation` and `SpyCloud_Conditional_Access_Playbook` playbooks must already be deployed in the same resource group
- The `AR_malware_25` and `AR_Breached_Users_20` analytic rules must already be deployed to the target Microsoft Sentinel workspace
- Each playbook's Managed Identity must have the **Microsoft Sentinel Responder** role on the workspace (grant this after deployment if not already assigned)

## Deployment

1. In the Azure Portal, navigate to **Deploy a custom template**
2. Select this template (`azuredeploy.json`)
3. Confirm Subscription and Resource Group
4. Enter the full resource ID of your Sentinel-enabled Log Analytics workspace for **Sentinel_Workspace_Resource_Id**
5. Leave the playbook name and analytic rule ID parameters at their defaults unless you renamed those resources during deployment
6. Click **Review + Create**, then **Create**

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| Sentinel_Workspace_Resource_Id | String | — | Full resource ID of the Sentinel-enabled Log Analytics workspace |
| MDE_PlaybookName | String | SpyCloud_MDE_Automation | Name of the MDE automation playbook Logic App |
| ConditionalAccess_PlaybookName | String | SpyCloud_Conditional_Access_Playbook | Name of the Conditional Access playbook Logic App |
| MalwareAnalyticRuleId | String | ead4deed-9d48-4646-aee0-6b46c2dd1ae6 | GUID of AR_malware_25 |
| BreachedUsersAnalyticRuleId | String | a25eba0e-ff42-4c97-a379-d76bdb2aa1e3 | GUID of AR_Breached_Users_20 |
| MDE_Automation_Rule_Order | Int | 1 | Execution order of the MDE automation rule |
| ConditionalAccess_Automation_Rule_Order | Int | 2 | Execution order of the Conditional Access automation rule |

After deployment, confirm both rules appear under **Microsoft Sentinel → Automation** and are enabled.
