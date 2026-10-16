# Tracked follow-up areas

These are curated future-work areas, not commitments, completed capabilities,
or a release guarantee. Scope, priority, ownership, and approval remain subject
to separate review.

This list records candidate known-limitations and follow-up work for the V1
PREVIEW toolkit.

## Publication security gate

Resolve security findings and independently re-review the corrected changes
before publishing. This is a publication gate, not optional roadmap work.
External ARM-TTK/Azure validation-service limitations, when encountered,
should be reported separately from toolkit code defects and do not by
themselves establish a toolkit fix is required.

## Recently completed in V1 PREVIEW

- **Make workbook `dependsOn` reference canonical parser IDs during packaging.**
  Bound reviewed workbook function prerequisites to actual
  `Microsoft.OperationalInsights/workspaces/savedSearches` resources in the
  same enclosing ARM template using canonical `[variables('parserObject<N>')._parserId<N>]`
  references (with literal `resourceId(...)` fallback), enforced unconditional
  parser installation, and verified exact resource mapping in packaging regressions.
- **Default hourly Sentinel rules to the native XDR lookback.** For supported
  rules with a one-hour Sentinel frequency and lookback, retained the hourly
  Custom Detection frequency (`PT1H`) and accepted the native four-hour
  ingestion-based lookback (`PT4H`) by default without pausing for timing-only
  approval, recording `eventTimeWindow` provenance and exact source/target
  hashes while keeping `parityClaimed: false`.
- **Map eligible Sentinel `kind: NRT` rules to Continuous (`PT0S`) Custom Detections.**
  Mapped eligible single-table `kind: NRT` rules to `kind: CustomDetection`
  with `schedule.frequency: "PT0S"` (`Edm.Duration` zero duration, while
  normalizing legacy `"NRT"` strings at Graph/ARM boundaries), surfacing
  incompatible multi-table, join, union, or aggregate NRT queries for explicit
  review.
- **Accept standard `_`-prefixed built-in ASIM parsers (`_ASim_*` and `_Im_*`).**
  Recognized built-in unifying ASIM parsers starting with `_` as supported in
  both Custom Detections and Defender Workbooks.
- **Inherit the solution release version for updated content & preserve lexical
  YAML version text.** Assigned generated/updated detections the solution
  release version in `[3.1.0, 4.0.0)` while preserving exact lexical
  `contentProvenance.source.version` strings and validating content hash
  identities.
- **Collect review feedback in one consolidated batch & guide users to the next
  migration blocker review.** Added `review-packet` / `consolidated-review-plan`
  CLI helpers and `nextStepRecommendation` / `nextBlockerReview` status and
  report summaries.
- **Set release-note dates predictably.** Defaulted release-note dates to
  today's date in `DD-MM-YYYY` format unless overridden.
- **Validate XDR Detections and Defender Workbooks in `.script/local-validation/`.**
  Added `validate-xdr-content.py` and `xdr-detection` / `xdr-workbook`
  validators to `build-and-validate.ps1` with explicit `SKIP` visibility.
- **Verify ARM templates through lab deployment by default (`lab-deployment`) with
  preflight preapproval.** Defaulted ARM validation to `lab-deployment` for
  Authoring and Qualification (with explicit `arm-ttk` selection supported in
  Authoring), added preflight preapproval prompts stating `X Sentinel rules,
  Y workbooks, and Z custom detections`, recorded target/SHA-256 deployment
  validation findings (`functionalQualificationVerified: false`,
  `alertParityVerified: false`), and surfaced `SKIP (lab-deployment selected as
  ARM validation route)` in `build-and-validate.ps1`.
- **Reconcile Qualification readiness and private configuration/support exports.**
  Added `assess_qualification_readiness` (separating `authorizationChecks`,
  `deploymentPermissionReadiness`, and `ingestionPermissionReadiness`) and
  `audit_private_config_and_support_export` to verify secret/private-target
  hygiene before export.
- **Add operator visibility, scheduled migration status reminders, single-owner
  execution leases, and safe approval forwarding.** Added
  `workflow-status-reminder` (with `suppressedNoChange`, workflow diagram, and
  batch duration explanation), `workflow-execution-owner`
  (`duplicate_executor_blocked` lease protection), and
  `workflow-forward-approval` (hash-bound `(runId, operation, approvedBy,
  forwardedToOwnerId, exactScope, approvalSha256)` forwarding).

## Candidate follow-ups

- **Deliver review-gate notifications reliably.** Add immediate coordinator-owned
  alerts when a solution needs review or release approval, with one consolidated
  decision request. Persist pending, delivered, and acknowledged notification
  states bound to the run ID and current review-packet hash. Generating a status
  summary must not count as delivery. Reconcile pending notifications after
  restart or model changes, and use one read-only fallback reminder schedule
  without creating another workflow executor. Deduplicate delivered unchanged
  alerts, but do not suppress undelivered requests. Test missed notifications,
  delivery failures, restart recovery, changed review packets, acknowledgment,
  and single-owner execution. The current status helper does not implement
  end-to-end scheduled notification delivery; separate maintainer implementation
  and verification are required.
- **Support automatic row-level query rewrite for `kind: NRT` rules with cosmetic
  `summarize` wrappers.** While single-table `kind: NRT` rules already map to
  `schedule.frequency: "PT0S"`, Sentinel NRT rules that include a trailing
  `summarize min(TimeGenerated), max(TimeGenerated), count() by ...` wrapper
  are flagged by Defender XDR's Continuous (NRT) engine restriction against
  `summarize`. Add a deterministic rewrite option to strip cosmetic timestamp/count
  aggregations into row-level projections when converting to `NRT`, falling back
  to `PT1H` scheduled frequency when aggregation is required.

Any future environment write remains separately gated by explicit approval
immediately before the exact operation. No cloud action is authorized by this
roadmap.
