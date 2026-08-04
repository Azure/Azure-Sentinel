# Upgrading to Digital Shadows v3.1.0

## Why upgrade?

Microsoft is shutting down the **HTTP Data Collector API** on **14 September 2026**. v3.0.0 uses it; v3.1.0 doesn't. Without this upgrade, your connector stops ingesting on that date.

## What changes

- Data lands in a new table: **`DigitalShadows_V2_CL`** (clean PascalCase columns).
- Old table `DigitalShadows_CL` stops receiving new data and ages out per your workspace retention.
- One new required deployment parameter: **`DcrWorkspaceResourceId`** (replaces the old `WorkspaceID` / `WorkspaceKey`).
- The Function Apps now use **managed identity** to write to Sentinel — no more shared workspace key.
- Function Apps now run **Python 3.11** (was 3.8).

If you only use the bundled workbook and rules, the upgrade is effectively transparent — the queries are migrated for you using KQL `project-rename` aliases.

## How to upgrade (5 minutes)

You need **Owner** or **User Access Administrator** on the resource group (same as v3.0.0).

1. In Microsoft Sentinel → **Content hub** → search **Digital Shadows** → click **Update**.
2. On the connector page click **Deploy to Azure**.
3. Fill in:
   - **DcrWorkspaceResourceId** — the full resource ID of your Log Analytics workspace.
     Find it: Log Analytics workspace → **Properties** → copy **Resource ID**.
     Format: `/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace>`.
   - Re-enter your SearchLight credentials (account ID, key, secret).
4. Wait for the deploy to finish (~2 min).
5. Sentinel → **Analytics** → **Rule templates** → find the two **Digital Shadows Incident Creation** templates → click each → **Create rule** → walk through the wizard with defaults → **Save**.

That's it. Data starts flowing to `DigitalShadows_V2_CL` on the next 10-minute timer fire.

## Verifying it worked

In Log Analytics → **Logs**:

```kql
DigitalShadows_V2_CL
| where TimeGenerated > ago(30m)
| take 5
```

If you see rows, you're done. If empty after 15 minutes, see Troubleshooting.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Deploy fails with `AuthorizationFailed` on role assignment | You don't have permission to assign roles in the RG | Ask whoever owns the subscription to grant you **User Access Administrator** (or **Owner**) on the RG, then re-run the deploy |
| Deploy fails: `DcrWorkspaceResourceId` invalid | You pasted a workspace ID GUID instead of the full resource ID | Use the full resource ID from the workspace's **Properties** blade — it starts with `/subscriptions/...` |
| Function App is Running but no rows appear in `DigitalShadows_V2_CL` | Either: SearchLight has no new events (most common), or the connector hasn't fired its first timer yet | Wait 10 min. Check **Application Insights → Logs**: `traces \| where operation_Name == "DigitalShadowsConnectorAzureFunction" \| take 50`. Look for `"got inside the poller code"` and `"Accepted"` |
| App Insights shows `ModuleNotFoundError: requests` or `azure.identity` | The Function App is running stale code | Restart the Function App: Portal → Function App → **Restart**. If still failing, redeploy the ARM template |
| App Insights shows `KeyError: 'DigitalShadowsAccountID'` | One of the SearchLight credential app settings is missing | Portal → Function App → **Environment variables** → verify all 4 are set: `DigitalShadowsAccountID`, `DigitalShadowsKey`, `DigitalShadowsSecret`, `DigitalShadowsURL` |
| My custom KQL hunting query / dashboard shows no new data | It still references `DigitalShadows_CL` | Update your query to `DigitalShadows_V2_CL` and use the new PascalCase column names. See the column mapping in `Workbooks/DigitalShadows.json` for examples |
| Sentinel incidents stop appearing for a particular detection | An analytic rule template wasn't activated after upgrade | Sentinel → **Analytics** → **Rule templates** → find the rule → **Create rule** → activate it |

## Column rename reference

If you have custom queries against the old table, here's the mapping:

| Old (v3.0.0) | New (v3.1.0) |
|---|---|
| `app_s` | `App` |
| `title_s` | `Title` |
| `raised_t` | `TimeRaised` |
| `updated_t` | `TimeUpdated` |
| `classification_s` | `Classification` |
| `risk_level_s` | `RiskLevel` |
| `risk_assessment_risk_level_s` | `RiskAssessmentRiskLevel` |
| `gm_link_s` | `GreyMatterLink` |
| `id_d` | `IncidentId` |
| `id_g` | `AlertId` |
| `status_s` | `Status` |
| `triage_id_g` | `TriageId` |
| `triage_raised_time_t` | `TriageRaisedTime` |
| `triage_updated_time_t` | `TriageUpdatedTime` |

## What's NOT changing

You don't need to:

- Migrate or back-fill old data from `DigitalShadows_CL`. It ages out per workspace retention. The connector will not re-pull historical events.
- Re-create your playbooks. They operate on Sentinel incidents, which work the same.
- Change anything in SearchLight itself. Credentials, API endpoints, classifications, and triage all work as before.
