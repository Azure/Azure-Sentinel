# App-Owner Notification

**Trust class: fully autonomous (read-only against Sentinel; sends a notification email
and calls a customer-provided lookup endpoint, no infrastructure or customer-facing state
change).**

Notifies the owner of the application/resource a new finding was matched to
(`ConfigId`), with an SLA deadline computed from the finding's severity.

## Flow

1. Triggers on Microsoft Sentinel incident creation.
2. Reads `Config_ID` and the incident's `severity` from the incident's custom details /
   incident properties.
3. Computes an SLA deadline from severity: Critical = 24h, High = 72h, Medium = 7d,
   Low/Info = 14d (default fallback).
4. If `Config_ID` is present, calls a parameterized HTTP lookup endpoint
   (`OwnerLookupApiUrl?configId=<ConfigId>`) expected to return
   `{ "ownerEmail": ..., "ownerDisplayName": ... }`.
5. Sends an email (Office 365 Outlook connector, "Send an email (V2)") to the resolved
   owner (or `FallbackNotificationRecipient` if no owner is resolved), with `Title`/
   `Severity`/`ResourceUrl`/`Solution` and the computed SLA deadline.
6. Logs the notification and SLA deadline back to the incident as a comment via the
   Microsoft Sentinel connector.
7. If `Config_ID` is absent, posts a comment noting the lookup/notification was skipped.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/PLACEHOLDER-RAW-GITHUB-URL-TO-azuredeploy.json)

*(Deploy-to-Azure button target is a placeholder — point it at this template's raw
GitHub URL once merged into `Azure/Azure-Sentinel`.)*

## Prerequisites

1. The Prancer Sentinel solution's Data Connector, Parser, and `PrancerFindings_CL` table
   must already be deployed and receiving data.
2. An analytic rule that sets `Config_ID` in `customDetails` must be enabled (today's
   published `SwarmHack High Confidence Critical Findings From Prancer` rule projects
   `Config_ID` in its query but does not yet list it under `customDetails:` — this needs
   to be added there, or in whichever rule(s) this playbook is attached to, for the
   lookup to have a `ConfigId` to work with).
3. **An owner-mapping data source.** This playbook does not ship one — Prancer does not
   maintain a ConfigId-to-owner directory today. You must either:
   - point `OwnerLookupApiUrl` at your own CMDB/ITSM owner-lookup API, or
   - replace the `Lookup_app_owner_via_HTTP_(customer-provided_endpoint)` action with a
     lookup against a Microsoft Sentinel Watchlist you populate with `ConfigId` →
     owner-email mappings (a Watchlist-based alternative to the HTTP call — swap the HTTP
     action for the Sentinel connector's "Get watchlist by alias"/"Get watchlist item"
     actions if you prefer not to stand up a separate HTTP endpoint).
4. An API key/token for the owner-lookup endpoint, if applicable (`OwnerLookupApiKey`).

## Post-Deployment steps

1. Authorize the `azuresentinel` and `office365` API connections created by this template.
2. Supply `OwnerLookupApiUrl` and `OwnerLookupApiKey` (or replace the lookup action per
   Prerequisite 3).
3. Set `FallbackNotificationRecipient` to a real monitored inbox (e.g., a SecOps
   distribution list), since unresolved-owner notifications will otherwise go to the
   placeholder address.
4. Attach this playbook to the relevant analytic rule(s) as an automation rule action in
   Microsoft Sentinel → Automation.
5. Test with both a resolvable and an unresolvable `ConfigId` to confirm the owner and
   fallback paths both notify correctly.

## Judgment calls / fallbacks used

- **Owner lookup**: implemented as a generic parameterized HTTP GET rather than a named
  CMDB/ITSM connector, since no specific customer owner-mapping system was specified.
  This is the primary "bring your own data source" surface in this playbook, called out
  explicitly per Prerequisite 3 above (including a Sentinel Watchlist as a concrete
  alternative wiring).
- **Notification channel**: chose the Office 365 Outlook "Send an email (V2)" action
  (high-confidence, ubiquitous connector shape) over a Teams direct-message action, since
  Teams "send a 1:1 chat message to a specific user" connector actions vary more by tenant
  configuration and were less certain to specify correctly here. Swapping to a Teams
  connector action is a straightforward substitution if preferred.
- **"Add comment to incident (V3)"**: same Microsoft Sentinel connector shape and caveat
  as in the Kill-Chain Context Enrichment playbook.
