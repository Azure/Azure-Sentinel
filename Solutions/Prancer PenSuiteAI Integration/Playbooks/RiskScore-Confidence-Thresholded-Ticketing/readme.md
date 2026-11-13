# RiskScore/Confidence-Thresholded Ticketing

**Trust class: fully autonomous (read-only against Sentinel; writes only to an external
ticketing system, no Azure infrastructure or customer resource state is changed).**

Auto-files a ticket only for findings where both independent SwarmHack scoring signals
clear a high bar (`RiskScore >= 8` and `Confidence >= 0.7` by default), rather than acting
on `RiskScore` alone. Findings below the bar are explicitly *not* ticketed — they are
routed to enrichment-only (see the Kill-Chain Context Enrichment playbook) instead of
generating ticket noise from uncertain AI output.

## Flow

1. Triggers on Microsoft Sentinel incident creation.
2. Reads `Risk_Score` and `Confidence` from the incident's custom details.
3. If both clear the configured thresholds (`RiskScoreThreshold`, default `8`;
   `ConfidenceThreshold`, default `0.7`):
   a. POSTs a ticket-creation request (`Title`/`Severity`/`CweId`/`Solution`/
      `ResourceUrl`/`KillChain`/`RiskScore`/`Confidence`) to a parameterized ticketing
      API endpoint.
   b. Parses the response for a ticket identifier.
   c. Writes the ticket ID back to the incident as a comment via the Microsoft Sentinel
      connector's "Add comment to incident (V3)" action.
4. If either threshold is not cleared, posts a comment explaining no ticket was filed and
   that the finding was routed to enrichment-only instead.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/PLACEHOLDER-RAW-GITHUB-URL-TO-azuredeploy.json)

*(Deploy-to-Azure button target is a placeholder — point it at this template's raw
GitHub URL once merged into `Azure/Azure-Sentinel`.)*

## Prerequisites

1. The Prancer Sentinel solution's Data Connector, Parser, and `PrancerFindings_CL` table
   must already be deployed and receiving data.
2. An analytic rule that sets `Risk_Score` and `Confidence` in `customDetails` (e.g.,
   `SwarmHack High Confidence Critical Findings From Prancer`) must be enabled.
3. A real ticketing system endpoint (ServiceNow Table API, Jira REST API, or equivalent)
   and an API key/token for it. **No real credentials are included in this template** —
   `TicketingApiUrl` and `TicketingApiKey` are parameters filled in at deployment time.
4. Decide and document your organization's actual `RiskScoreThreshold` /
   `ConfidenceThreshold` values if different from the defaults (`8` / `0.7`).

## Post-Deployment steps

1. Authorize the `azuresentinel` API connection created by this template.
2. Supply `TicketingApiUrl` and `TicketingApiKey` as secure deployment parameters (e.g.,
   via Key Vault reference) — never commit real values into source control.
3. Adjust the `File_ticket_via_HTTP_(generic_ServiceNow/Jira-style_endpoint)` action's
   request body field names to match your actual ticketing system's schema (the shipped
   body uses generic field names — `short_description`, `severity`, `description`, etc.
   — that read naturally for ServiceNow but may need renaming for Jira or another system).
4. Attach this playbook to the relevant analytic rule(s) as an automation rule action in
   Microsoft Sentinel → Automation.
5. Test with a low-`RiskScore`/low-`Confidence` incident and a high/high incident to
   confirm both branches (no-ticket comment vs. filed-ticket comment) behave as expected.

## Judgment calls / fallbacks used

- **Ticketing action**: modeled as a generic HTTP POST to a parameterized endpoint rather
  than a named ServiceNow or Jira connector, since no real ticketing credentials or tenant
  were available to build/validate against a specific connector. The request/response body
  shapes are illustrative placeholders (ServiceNow-flavored field names) — **this is the
  primary "swap for your real system" surface in this playbook** and is called out
  explicitly rather than presented as a working integration.
- **"Add comment to incident (V3)"**: same Microsoft Sentinel connector shape and caveat
  as in the Kill-Chain Context Enrichment playbook.
- Thresholds read directly from the triggering incident's custom details rather than
  re-querying `PrancerFindings()`, since the values that gated the analytic rule's alert
  are already present at incident-creation time and re-querying would only reintroduce a
  potential race against newer scan data.
