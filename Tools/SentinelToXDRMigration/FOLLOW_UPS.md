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
- **Enforce clean workbook publication (`public-workbook-v1`) and Marketplace
  customer usage attribution discovery (`trackingId`).** Added
  `workbook-publication-plan` and `workbook-publication-clean` so published
  `XDR Workbooks/*.json` strip authoring review metadata while preserving
  dependency provenance, added anonymous Marketplace catalog discovery and
  persistence of `SolutionMetadata.json` `trackingId` in V3.1 packaging, and
  preserved `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1`
  unchanged from `upstream/master` (with optional legacy V3 compatibility
  routing in `.script/package-automation/package-generator.ps1`).
- **Default all workflow entry points and agent adapters to `authoring`.**
  Aligned CLI (`workflow-init`), canonical workflow instructions, and agent
  adapters (`AGENTS.md`, `CLAUDE.md`, `.github`, `.claude`, `.cursor`, and
  `.windsurf`) to default to the `authoring` profile and route packaging through
  `package-v3-1` (V3.1).
- **Organize Python implementation into `solution_manager` capability subfolders.**
  Moved the 53 implementation modules into `solution_manager/` grouped by
  capability (`core/`, `authoring/`, `migration/`, `qualification/`,
  `packaging/`, `reporting/`, and `research/` scaffold) with `cli.py` at the
  package root and backwards-compatible `sentinel_xdr_migration` module aliases.

## Candidate follow-ups

- **Preserve non-Log-Analytics query types and Azure resource-protection pickers
  in Defender workbooks by default.** Defender workbooks should convert Sentinel
  Log Analytics KQL queries to Advanced Hunting while leaving other query types
  (such as Azure Resource Graph `microsoft.resourcegraph/resources`) unchanged.
  When a resource/subscription picker scopes protected Azure resources (such as
  AKS clusters or Azure subscriptions being protected) rather than selecting
  Sentinel workspaces, keep that picker working unchanged after migration by
  default.
- **Extend conversion logic to migrate `SecurityAlert` and `SecurityIncident`
  queries to `AlertInfo` and `AlertEvidence` (`AlertEntities`) tables.** Add
  deterministic table and column conversion rules for `SecurityAlert` and
  `SecurityIncident` queries into Defender XDR `AlertInfo` and `AlertEvidence`
  (`AlertEntities`) tables across rules and workbooks.
- **Safely capture user decisions into the submitted work for all flows under
  Solution Manager.** Project sanitized, hash-bound reviewer decisions,
  waivers, exclusions, and rationale across authoring, migration, qualification,
  and future Solution Manager flows into the submitted solution PR artifacts
  (without exposing private tenant, workspace, or environment identifiers).
- **Add catalog-specific validation routing for `Sample Data/Tables/` in
  `.script/sampleDataValidator.ts`.** `.script/sampleDataValidator.ts` currently
  validates modified JSON files under `Sample Data/` as connector log arrays
  and rejects email literals other than `sanitized@sanitized.com`. Because
  `Sample Data/Tables/<TableName>/base-event.json` and `metadata.json` are
  single JSON objects required by `_load_table_base`, add catalog-specific
  schema and sanitation validation in `.script/sampleDataValidator.ts` for
  `Sample Data/Tables/` rather than wrapping catalog objects in arrays.
- **Promote `qualification` to the default workflow profile once end-to-end
  qualification flow runs fluently.** All tools and agent adapters currently
  default to `authoring` and ask before optional lab `qualification`; switch
  the default profile to `qualification` once live workspace provisioning,
  synthetic ingestion, and parity orchestration are fluent end-to-end.

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
