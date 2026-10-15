# Kill-Chain Context Enrichment

**Trust class: fully autonomous (read-only, no infrastructure or customer-facing state change).**

Posts a formatted, read-only comment on a Microsoft Sentinel incident summarizing the
SwarmHack-specific context (`KillChain`, `CrownJewels`, `RiskScore`, `Confidence`,
`Solution`) for the finding that generated it. This playbook never modifies infrastructure,
never contacts an external system, and never takes any action beyond commenting on the
incident it was triggered from.

## Flow

1. Triggers on Microsoft Sentinel incident creation (`Microsoft Sentinel` connector,
   `When Azure Sentinel incident creation rule was triggered`).
2. Reads `UniqueFindingId` from the incident's custom details (populated today by the
   `SwarmHack High Confidence Critical Findings From Prancer` analytic rule's
   `customDetails.UniqueFindingId`; any rule that sets this custom detail can trigger this
   playbook).
3. If `UniqueFindingId` is present, queries `PrancerFindings()` for that finding's
   `KillChain`/`CrownJewels`/`RiskScore`/`Confidence`/`Solution`/`Title`/`Severity`.
4. Formats the result into an HTML summary.
5. Posts the summary as an incident comment via the Microsoft Sentinel connector's
   "Add comment to incident (V3)" action.
6. If `UniqueFindingId` is absent, posts a short comment noting enrichment was skipped instead
   of failing silently.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/PLACEHOLDER-RAW-GITHUB-URL-TO-azuredeploy.json)

*(Deploy-to-Azure button target is a placeholder — point it at this template's raw
GitHub URL once merged into `Azure/Azure-Sentinel`.)*

## Prerequisites

1. The Prancer Sentinel solution's Data Connector, Parser (`PrancerFindings`), and
   `PrancerFindings_CL` table must already be deployed and receiving data (Phase 1 of
   this content effort).
2. At least one analytic rule that sets `UniqueFindingId` in `customDetails` (e.g.,
   `SwarmHack High Confidence Critical Findings From Prancer`) must be enabled, since this
   playbook depends on that custom detail to know which finding to enrich.
3. The Log Analytics workspace GUID (`WorkspaceId` parameter) hosting `PrancerFindings_CL`.
4. Permission to create a Logic App and an `azuresentinel` API connection in the target
   resource group.

## Post-Deployment steps

1. Authorize the `azuresentinel` API connection created by this template (Azure Portal →
   the connection resource → "Edit API connection" → Authorize), unless you deploy with
   an existing pre-authorized connection.
2. Grant the Logic App's system-assigned managed identity **Log Analytics Reader**
   (or **Monitoring Reader**) on the Log Analytics workspace identified by `WorkspaceId`
   — the playbook queries `PrancerFindings()` via the Log Analytics Query API
   (`https://api.loganalytics.io`) using that identity, not the `azuresentinel`
   connection.
3. Attach this playbook to the relevant analytic rule(s) as an automation rule action
   ("Run playbook") in Microsoft Sentinel → Automation, scoped to incidents created from
   Prancer-sourced analytic rules.
4. Confirm a test incident produces a readable enrichment comment before enabling broadly.

## Judgment calls / fallbacks used

- **Log Analytics query action**: instead of the Azure Monitor Logs connector's
  connector-specific "Run query and list results" action (whose exact `operationId`/`path`
  values could not be confirmed with certainty here), this playbook uses a generic HTTP
  action against the documented Log Analytics Query API
  (`POST https://api.loganalytics.io/v1/workspaces/{id}/query`), authenticated via the
  Logic App's system-assigned managed identity. This is a deliberate, clearly-structured
  fallback rather than a guessed connector action name — swap for the native Azure Monitor
  Logs connector action during deployment if preferred.
- **"Add comment to incident (V3)"**: modeled on the standard Microsoft Sentinel connector
  shape used broadly across published Sentinel playbook templates. Reconcile the exact
  `path`/`apiVersion` against your tenant's connector definition in Logic Apps Designer
  before first deployment.
