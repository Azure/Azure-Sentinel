# Teams Approval-Gated Notification

**Trust class: human-approval-gated (the one exception in this inventory to
"fully autonomous"). This playbook changes state — it posts to Teams and writes an
audit-log comment — but it does NOT execute any remediation action.**

Posts an adaptive card to a Microsoft Teams channel for incidents where `CrownJewels` is
non-empty (i.e., a SwarmHack kill chain reached a declared high-value asset), with
Approve/Reject buttons, and blocks on a real human response before logging anything back
to the incident. If nobody responds within the timeout window, it escalates to a fallback
on-call notification instead of silently expiring.

**What this playbook deliberately does NOT do:** it does not execute any follow-up
remediation action on Approve. Today, "Approve" only produces an audit-trail comment
recording who approved it and when. Wiring a real remediation action (e.g., quarantining
a resource, disabling an account, rotating a credential) behind the Approve button is an
explicit **TODO / extension point**, not an oversight — see "Judgment calls" below and the
governing ADR (`docs/ADR-sentinel-solution-content-enrichment.md`, Tier 3) for why this is
scoped as approval-gate mechanics only in this pass.

**What this playbook is explicitly NOT**: it is not, and must never be extended into, an
auto-triggered re-scan/re-verification playbook that launches a new SwarmHack
exploitation run off an alert. That capability is explicitly out of scope for this ADR and
requires its own separate ADR plus product/legal sign-off (see the governing ADR's
Consequences and Concrete Implementation Plan, Tier 3). Do not add a "re-verify with
SwarmHack" action to this playbook's Approve branch without that separate review.

## Flow

1. Triggers on Microsoft Sentinel incident creation.
2. Reads `Crown_Jewels`, `Kill_Chain`, `Risk_Score`, `Confidence`, and `URL` from the
   incident's custom details.
3. If `Crown_Jewels` is non-empty:
   a. Composes an Adaptive Card (v1.4) summarizing `KillChain`/`CrownJewels`/`RiskScore`/
      `Confidence`/`ResourceUrl`, with `Approve` and `Reject` `Action.Submit` buttons.
   b. Posts it to a Teams channel and **waits for a response**, using the Teams
      connector's "Post adaptive card and wait for a response" action with a configurable
      timeout (`ApprovalTimeout`, default `PT4H` / 4 hours).
   c. On a response (Approve or Reject), parses the responder's identity and choice, and
      logs "APPROVED by X at timestamp" or "REJECTED by X at timestamp" back to the
      incident as a comment via the Microsoft Sentinel connector. No remediation action is
      taken in either case.
   d. On timeout (or if the wait action fails/is skipped), sends an escalation email to
      `FallbackEscalationRecipient` and logs the escalation to the incident as a comment.
4. If `Crown_Jewels` is empty, posts a comment noting the approval flow did not trigger.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/PLACEHOLDER-RAW-GITHUB-URL-TO-azuredeploy.json)

*(Deploy-to-Azure button target is a placeholder — point it at this template's raw
GitHub URL once merged into `Azure/Azure-Sentinel`.)*

## Prerequisites

1. The Prancer Sentinel solution's Data Connector, Parser, and `PrancerFindings_CL` table
   must already be deployed and receiving data.
2. An analytic rule that sets `Crown_Jewels`, `Kill_Chain`, `Risk_Score`, `Confidence`, and
   `URL` in `customDetails` must be enabled — `SwarmHack High Confidence Critical Findings
   From Prancer` sets all five today. If you attach this playbook to a different rule, make
   sure that rule's `customDetails:` includes the same five keys or the approval card will
   have missing data.
3. A Microsoft Teams team and channel to post approval cards to, and the ability to obtain
   its `TeamsGroupId`/`TeamsChannelId`.
4. Explicit internal sign-off on **who is authorized to approve/reject** these cards and
   what "Approve" is understood to mean operationally, before enabling this in a
   production tenant — this playbook logs the approval, it does not define or enforce your
   organization's approval policy.
5. A monitored fallback escalation mailbox for the timeout path (`FallbackEscalationRecipient`).

## Post-Deployment steps

1. Authorize the `azuresentinel`, `teams`, and `office365` API connections created by this
   template.
2. Verify the Teams connector's "Post adaptive card and wait for a response" action
   resolves correctly against your tenant's Teams connector API version in Logic Apps
   Designer (see Judgment calls below) — reconcile the `path`/`queries` values in the
   template if your tenant's connector surface differs.
3. Restrict who can respond to the posted adaptive card to your intended approver group
   (Teams channel membership, or a dedicated approvals channel) — this playbook trusts
   whatever identity Teams reports as the responder.
4. Attach this playbook to the relevant analytic rule(s) as an automation rule action in
   Microsoft Sentinel → Automation, scoped specifically to crown-jewel-reaching incidents.
5. Test the full loop at least three times before production use: an Approve response, a
   Reject response, and a deliberate timeout (leave the card unanswered past
   `ApprovalTimeout`) to confirm the escalation email and incident comment both fire.
6. Document, outside this playbook, what your team's actual process is when a remediation
   action is eventually wired to the Approve branch (see TODO below) — this is a process
   design question, not something this pass resolves.

## Judgment calls / fallbacks used

- **"Post adaptive card and wait for a response"**: this is the one action in this
  inventory built with the lowest confidence in its exact `path`/`queries`/response-schema
  values. The Teams connector's wait-for-response adaptive-card action is real and widely
  used in published Sentinel/Logic Apps playbooks, but the precise `operationId`/`path`
  string varies by connector API version, and could not be confirmed with certainty in
  this pass. **Do not treat the literal JSON as final** — reconcile it against Logic Apps
  Designer (Insert an action → Microsoft Teams → "Post adaptive card and wait for a
  response") for your tenant's connector version before first deployment. The structural
  pattern used here (an `ApiConnectionWebhook` with a `limit.timeout`, followed by
  branches keyed off the action's `Succeeded` vs. `TimedOut`/`Failed`/`Skipped` status) is
  the genuinely correct Logic Apps mechanism for a real wait-with-timeout human-in-the-loop
  gate, independent of the exact connector action name.
- **Parsed responder identity fields** (`responder.displayName`/`responder.email`,
  `data.action`, `submitActionId`): the exact response JSON shape returned by the wait
  action is likewise not confirmed with certainty; the `Parse_approval_response` action's
  schema is a reasonable, clearly-structured best guess. Validate against a real test
  response payload during deployment and adjust the schema/expressions if the actual
  shape differs.
- **No remediation action on Approve**: deliberate, per the governing ADR's Tier 3 scope —
  built as an explicit extension point (see the "What this playbook deliberately does NOT
  do" section above), not an oversight.
- **"Add comment to incident (V3)"**: same Microsoft Sentinel connector shape and caveat
  as in the Kill-Chain Context Enrichment playbook.
- **Escalation channel**: chose email (Office 365 Outlook "Send an email (V2)", high
  confidence) over a second Teams post for the timeout-escalation path, on the reasoning
  that an unaddressed Teams card most plausibly means the primary channel isn't being
  monitored closely enough — escalating to a different channel (email) rather than the
  same one that already timed out.
