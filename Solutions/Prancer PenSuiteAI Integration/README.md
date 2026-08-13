# Prancer PenSuiteAI Integration — draft rewrite

Staged, reviewed draft of the modernized content for
`Solutions/Prancer PenSuiteAI Integration/` in the public `Azure/Azure-Sentinel`
repo, per `docs/ADR-sentinel-solution-modernization.md`. This directory
mirrors that target path (minus `Package/`, see below) so it can be dropped
into a real clone of `Azure/Azure-Sentinel` when the PR is ready to go out.

**This has not been pushed or opened as a PR anywhere.** It's preserved here
(in our own repo, with git history) rather than left in an ephemeral
scratchpad, specifically so the work survives independent of any one
session/environment. Submitting it to Microsoft's public repo is a separate,
explicitly gated step pending direct approval — see the ADR's "Open
Questions."

## What's here

- `Parsers/PrancerFindings.yaml` — the parser function, centralizing severity
  ranking, payload extraction, and data-quality flagging.
- `Analytic Rules/*.yaml` + `Hunting Queries/*.yaml` — rewritten to query
  through `PrancerFindings` against the native `PrancerFindings_CL` schema.
  Phase 1 fixed two real bugs found in the process: a snapshot-type filter
  that only checked the first array element before expanding all of them
  (all 10 CSPM resource-type rules), and a field-name mismatch between
  `PAC_High_Severity.yaml` and its hunting-query counterpart
  (`data_alert_mitreId_s` vs. `data_alert_cvss_mitreId_s` — both now
  reference the same function-derived `MitreIds`). Phase 2 (per
  `docs/ADR-sentinel-solution-content-enrichment.md`) consolidated the
  per-resource-type CSPM rules into finding-class rules and added
  correlation, confidence-weighted, and kill-chain-aware rules and hunting
  queries that query `RiskScore`, `Confidence`, `KillChain`, and
  `CrownJewels` — fields the Phase 1 package ingested but never surfaced.
- `Workbooks/PrancerSentinelAnalytics.json` — Phase 1 rewrote all 28 tiles
  against the function; ~130 dead conditional-formatting/hide-column rules
  and all commented-out dead KQL removed (2849 → ~1090 lines); a new "Data
  Quality Issues" tile added. Phase 2 added kill-chain, crown-jewel, and
  MITRE-coverage visualizations (attack-path Sankey, crown-jewel exposure
  and blast-radius views, "confirmed vs. theoretical" ATT&CK coverage, and
  related tiles).
- `Data Connectors/PrancerLogData.json` — corrected to describe the real
  push/DCR mechanism (was: contradictory shared-key + Azure-Functions-poll
  claims, neither true). `Data Connectors/PrancerConnectivityHealthCheck/`
  — new in this pass: an optional, real Azure Function (Timer-triggered,
  every 6h) that independently verifies `PrancerFindings_CL` ingestion is
  still flowing and reports via a webhook that does not depend on the same
  DCR being healthy, plus an optional status row in a separate
  `PrancerConnectivityHealth_CL` table via its own DCE/DCR. Gives the
  connector a real deployable artifact rather than just a description.
- `Watchlists/CrownJewelAssets.json` — new in this pass: a "Prancer Crown
  Jewel Assets" watchlist template (schema verified against real shipping
  solutions in `Azure/Azure-Sentinel`, not guessed) so customers can declare
  asset criticality independent of SwarmHack engagement history. Consumed by
  `Analytic Rules/Watchlist_CrownJewel_Match_Escalation.yaml`, which
  escalates ANY finding — not just SwarmHack's own — that matches a
  watchlist-declared crown jewel.
- `Playbooks/` — new in Phase 2, trust-tiered per
  `docs/ADR-sentinel-solution-content-enrichment.md` Tier 3: fully
  autonomous, read-only automation (kill-chain-context incident enrichment,
  confidence-thresholded ticketing, executive digest, app-owner
  notification) plus one human-approval-gated notification playbook for
  crown-jewel-reaching findings. No auto-triggered action-taking automation
  (e.g. a re-scan/re-verification playbook) is included — that capability is
  explicitly deferred to a future ADR. Each playbook has its own `readme.md`
  with deployment/prerequisite/post-deployment steps.
- `Data/Solutions_PrancerLogIntegration.json` — build-manifest fixes (naming,
  stuck version, filename-casing bug, missing `Parsers` entry).
- `ReleaseNotes.md` — `4.0.0` row (major bump: breaking schema change),
  `4.1.0` row (Phase 2 content enrichment), and `4.2.0` row (Watchlist +
  connectivity health-check Function).

## What's NOT here

`Package/mainTemplate.json` / `createUiDefinition.json` / `testParameters.json`
are intentionally untouched and not copied here — they must be regenerated
via `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1` in an
environment with PowerShell available (not available in the environment that
produced this draft). The target repo's own contribution guide explicitly
forbids hand-editing `mainTemplate.json`. **This is a hard blocker before a
real PR can be opened** — do not attempt to hand-write these files.

## Known, honest gaps (carried from the ADR, not new)

- ~10 OWASP-category-keyed tag columns have no source data in the current
  schema and were already a documented gap before this rewrite — not
  reintroduced, not newly broken.
- A few legacy fields (WASC ID, a `description` field distinct from `Title`,
  compliance-framework tags) have no equivalent in the new schema and were
  dropped or backfilled from `Title` — called out inline via comments in the
  affected files.

## Before this becomes a real PR

1. Run `createSolutionV3.ps1` (or `.script/local-validation/build-and-validate.ps1`)
   in an environment with `pwsh` to regenerate `Package/` and get real
   ARM-TTK/detection-schema/KQL CI validation — none of that ran here.
2. Verify the `isnotempty(Snapshots)` CSPM-vs-pentest discriminator in
   `PrancerFindings.yaml` against real ingested data (inferred from the
   Payload shape, not a live `ScanType` enum).
3. Product sign-off on the repurposed "infra findings by severity" tile
   (previously "Pass/Fail" — no pass/fail concept survives in the new
   schema).
4. **Audit the connector logo SVG against Microsoft's published solution-logo
   requirements** (no inline styles, no design-tool export artifacts, ≤5KB,
   no `<title>` tag, GUID-only `id` attributes). The logo is referenced by
   URL (`https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/Prancer.svg`
   via `Data/Solutions_PrancerLogIntegration.json`) rather than stored as a
   file in this repo, so its bytes cannot be audited from here — this must be
   pulled from the target `Azure/Azure-Sentinel` repo (or wherever the
   canonical source SVG lives) and checked/cleaned before the external PR is
   opened.
