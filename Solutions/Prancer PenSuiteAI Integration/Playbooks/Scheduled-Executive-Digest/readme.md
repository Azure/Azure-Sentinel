# Scheduled Executive Digest

**Trust class: fully autonomous (read-only against Sentinel/Log Analytics; sends an
email, no infrastructure or customer-facing state change).**

Runs weekly and emails a board-deck-ready summary of the trailing week's Prancer
findings: new Critical/High count, average `RiskScore` trend delta (SwarmHack), top
recurring `KillChain` patterns, and crown-jewel exposure count.

## Flow

1. Triggers on a weekly recurrence (default: every Monday 08:00 UTC — configurable by
   editing the `Weekly_recurrence` trigger's `schedule` after deployment).
2. Queries `PrancerFindings()` for the trailing 7 days, computing:
   - count of new Critical/High findings,
   - crown-jewel exposure count (findings with non-empty `CrownJewels`),
   - average `RiskScore` delta for `swarmhack` findings vs. the prior 7-day window,
   - the top 5 recurring `KillChain` values by count.
3. Formats the result into an HTML digest.
4. Sends the digest via the Office 365 Outlook connector's "Send an email (V2)" action to
   a parameterized recipient list.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/PLACEHOLDER-RAW-GITHUB-URL-TO-azuredeploy.json)

*(Deploy-to-Azure button target is a placeholder — point it at this template's raw
GitHub URL once merged into `Azure/Azure-Sentinel`.)*

## Prerequisites

1. The Prancer Sentinel solution's Data Connector, Parser, and `PrancerFindings_CL` table
   must already be deployed and receiving data (a full trailing week of data is needed for
   a meaningful first digest).
2. The Log Analytics workspace GUID (`WorkspaceId` parameter) hosting `PrancerFindings_CL`.
3. An Office 365 (or equivalent Exchange Online) mailbox to send from, and permission to
   create an `office365` API connection.
4. The distribution list or set of recipient addresses for `DigestRecipients`.

## Post-Deployment steps

1. Authorize the `office365` API connection created by this template with an account that
   has send permission (a shared mailbox or service account is recommended over a named
   individual's mailbox).
2. Grant the Logic App's system-assigned managed identity **Log Analytics Reader** (or
   **Monitoring Reader**) on the Log Analytics workspace identified by `WorkspaceId`.
3. Adjust the `Weekly_recurrence` trigger's day/hour/timezone if Monday 08:00 UTC does not
   match your organization's reporting cadence.
4. Send a manual test run (Logic App → Run Trigger) and confirm the digest email renders
   correctly and the numbers are sane before leaving it on recurring schedule.

## Judgment calls / fallbacks used

- **Log Analytics query action**: same generic-HTTP-against-the-Log-Analytics-Query-API
  fallback used in the Kill-Chain Context Enrichment playbook, for the same reason (avoiding
  a guessed Azure Monitor Logs connector `operationId`). Swap for the native connector
  action if preferred.
- **Email delivery**: uses the Office 365 Outlook connector's "Send an email (V2)" action
  (a very standard, high-confidence connector shape). A generic SMTP/HTTP action is a
  reasonable alternative if the target tenant doesn't use Exchange Online — not built here
  since Office 365 Outlook is the more common case for Sentinel-adjacent tenants.
- The trailing-week KQL query computes the prior-week `RiskScore` average via a `toscalar`
  subquery for the delta calculation; if `PrancerFindings_CL` volume is very low in a given
  week (e.g., a new customer with limited scan history), the delta may be based on very few
  data points — this is a known limitation of a fixed 7-day comparison window, not a bug.
