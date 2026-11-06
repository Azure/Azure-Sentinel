---
name: validate-sentinel-workbook-browser
description: 'Validate and test Microsoft Sentinel workbooks in the Microsoft Defender portal at security.microsoft.com using Playwright or browser MCP. Use for workbook rendering, data panels, parameters, tabs, conditional visibility, filter propagation, drill-through, reset, screenshots, and browser qualification. Requires fresh tenant/workspace confirmation and separate live-execution approval; offline tests never qualify authenticated portal behavior.'
---

# Validate a Microsoft Sentinel workbook in the browser

Follow the [Sentinel workbook testing walkthrough](../../../Tools/SentinelToXDRMigration/docs/workbook-browser-testing.md).
For solution Qualification, also follow the [canonical workflow](../../../Tools/SentinelToXDRMigration/agent-workflows/end-to-end-migration.md#workbook-qualification-and-browser-qa).
This skill coordinates existing tools; it does not replace their approval,
target, provenance, query, packaging, or evidence contracts.

## Scope and approval

1. Identify the exact workbook, source revision/hash, expected panels and
   interactions, and requested coverage. Native Sentinel workbooks do not
   require conversion to `XDR Workbooks` or an invented AR/CD pair.
2. Default to offline inspection. Before any live metadata read, browser
   navigation, query, or capture, ask for fresh confirmation of the exact
   non-production tenant, subscription, workspace, workbook instance, portal
   URL, bounded interactions and time window. Use structured questions.
   A missing, unavailable, declined or cancelled response pauses live work,
   even in autopilot. A configured target, existing browser login, maintainer
   authorization, or previous run is not approval for this run.
3. For existing Qualification, consume the selected run's locked
   `qualification-target.json`; never discover alternatives or silently
   retarget it. Ask the user to authenticate manually. Never handle passwords,
   MFA, tokens or cookies in chat, automate sign-in, or switch directories.
4. Prefer `https://security.microsoft.com` and **Microsoft Sentinel >
   Threat management > Workbooks**. Observe the actual page and frames with
   browser snapshots before choosing unique controls; do not copy Azure
   portal account-menu/iframe selectors or invent a Defender deep link.
   Verify the visible authenticated tenant/workspace and installed workbook
   identity against the approved target, not merely the address bar.
5. **Open in Azure** is a separate, explicitly approved fallback for
   visualizations unavailable in Defender. Reverify the same tenant,
   workspace and workbook after the transition. Never silently fall back
   and call an Azure-only result a Defender-portal pass.

## Execute bounded checks

- Read the walkthrough's coverage matrix and agree exact expected results
  before execution. Inspect original JSON and dependency metadata without
  editing queries, parameters, defaults, exports, or production content.
- Use `workbook-query-plan/review/execute` and
  `workbook-ui-plan/review/execute` where the existing CLI supports the
  selected content. Require the current reviewed browser configuration,
  private session binding and real provider. If unsupported or blocked,
  preserve that result; do not hand-edit workflow state or fabricate receipts.
- For standalone Sentinel testing, use available Playwright/browser MCP
  tools after approval and live identity verification. Inspect snapshots,
  scoped controls, rendered results, console and failed requests. Manual
  MCP observations are standalone evidence, not an automatic CLI acceptance.
  Only explicitly reviewed external evidence may enter `workbook-ui-import`.
- Check rendering and query errors separately. Exercise applicable parameter
  changes, dependent refresh, tabs, conditional sections, filter propagation,
  drill-through and reset. Assert the resulting data and preserved scope,
  not just successful clicks. Hidden values need observable evidence; display
  labels alone cannot prove a workspace/resource identifier.
- Stop on ambiguous controls, identity change, navigation outside scope,
  query/JavaScript errors, unavailable data, unexpected writes, unsupported
  assertions or timeout. Later checks remain not-run. No retries against
  same-named controls in another frame, no success-shaped fallback.
- Do not click **Save**, **Save as**, **Edit**, install Content Hub content,
  deploy, ingest telemetry, enable rules or perform destructive actions.
  Testing an already installed workbook is read/observe scope; provisioning
  prerequisites belong to a separately approved workflow.

## Evidence and privacy

Screenshots are disabled by default. If requested, prefer local conservative
redaction. Agree exact capture scope and masking before capture, including
parent-page overlays and workbook frames. If reliable masking cannot be
established, do not capture. Manual or unredacted local capture requires
specific approval; never upload sensitive portal content to external AI
services. Review the final image before sharing; discard failed captures.
Do not export storage state, cookies, request headers/bodies, record values,
account identities or tenant identifiers into PR evidence.

Report source hash/revision, tested portal, coverage counts, expected versus
observed assertions, sanitized errors, accepted data limits, and remaining
checks as passed/failed/blocked/not-run/not-applicable. Explain no-data and
truncation explicitly. Distinguish offline/synthetic, authenticated
standalone MCP, and accepted toolkit Qualification evidence. A smoke pass,
configured provider, imported boolean or previous source hash is not proof
of current authenticated data/interaction behavior.
