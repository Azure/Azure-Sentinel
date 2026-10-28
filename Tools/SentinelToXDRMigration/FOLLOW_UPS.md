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
- **Preserve non-Log-Analytics query types and Azure resource-protection pickers
  in Defender workbooks by default.** Preserved Azure Resource Graph (`queryType: 1`,
  `microsoft.resourcegraph/resources`) tiles and kept `{subscription}` /
  resource-protection pickers active when referenced by preserved non-Log-Analytics
  queries (`preservedByResourceProtectionQueries`).
- **Extend conversion logic to migrate `SecurityAlert` and `SecurityIncident`
  queries to `AlertInfo` and `AlertEvidence` (`AlertEntities`) tables.** Added
  deterministic table and column conversion rules (`SystemAlertId -> AlertId`,
  `AlertName/DisplayName -> Title`, `AlertSeverity -> Severity`,
  `ProviderName -> DetectionSource`, `ProductName -> ServiceSource`,
  `Tactics -> AttackTechniques`/`Category`, `TimeGenerated -> Timestamp`) with
  `AlertEvidence` left-outer join synthesis across rules and workbooks.
- **Support automatic row-level query rewrite for `kind: NRT` rules with cosmetic
  `summarize` wrappers.** Added deterministic `rewrite_cosmetic_nrt_summarize`
  to convert trailing timestamp/count `summarize` wrappers into row-level
  projections while preserving `schedule.frequency: "PT0S"`, and automatically
  fell back behavioral `summarize` NRT rules to `PT1H` / `PT4H`.
- **Add catalog-specific validation routing for `Sample Data/Tables/` in
  `.script/sampleDataValidator.ts`.** Routed `Sample Data/Tables/<TableName>/base-event.json`
  and `metadata.json` through `IsValidTableCatalogSampleData` and RFC 2606 /
  contoso / example email sanitation checks.
- **Safely capture user decisions into the submitted work for all flows under
  Solution Manager.** Added `solution_manager.reporting.decision_manifest`
  (`decision-manifest-v1`) with fail-closed privacy verification and
  `decisionManifestSummary` projection into solution reports.
- **Deliver review-gate notifications reliably.** Added
  `solution_manager.core.review_notifications` to persist `pending`,
  `delivered`, `acknowledged`, and `delivery_failed` notification states bound
  to `(runId, reviewPacketSha256)` with restart reconciliation and deduplication.
- **Implement 5-stage end-to-end `QualificationOrchestrator` and promotion gate.**
  Added `solution_manager.qualification.orchestrator` (`preflight`,
  `deployment`, `mock_ingestion`, `rule_parity`, `workbook_qualification`) and
  `evaluate_qualification_promotion_gate` to verify end-to-end qualification
  readiness before promoting `qualification` as the default profile.
- **Raise minimum V3.1 solution release version floor to `>= 3.2.2 and < 4.0.0`.**
  Updated V3.1 solution version policy documentation and workflow examples to
  require canonical solution versions in `[3.2.2, 4.0.0)`.
- **Add cross-surface `AlertEvidence` Azure resource column compatibility aliases
  and document deterministic `SecurityAlert`/`SecurityIncident` mappings.**
  Added `ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS` using
  `coalesce(tostring(column_ifexists(...)))` so migrated `SecurityAlert` and
  `SecurityIncident` queries referencing `ResourceID`/`AzureResourceId`,
  `ResourceType`/`AzureResourceType`, or `SubscriptionId`/`AzureSubscriptionId`
  execute identically across Defender XDR Advanced Hunting and Azure Monitor /
  Sentinel Log Analytics.
- **Bundle Microsoft Graph Bicep/ARM template (`grant-graph-hunting-scopes.arm.json`)
  and `build_missing_graph_scope_arm_offer` remediation helper.** Added bundled
  `grant-graph-hunting-scopes.bicep` and `grant-graph-hunting-scopes.arm.json`
  templates under `solution_manager/qualification/templates/` and
  `build_missing_graph_scope_arm_offer` to offer explicit-approval deployment of
  `Microsoft.Graph/applications@v1.0`, `servicePrincipals@v1.0`, and
  `oauth2PermissionGrants@v1.0` when `ThreatHunting.Read.All` or
  `CustomDetection.ReadWrite.All` is missing.

- **Flip default workflow profile from `authoring` to `qualification`.**
  Switched the default `--workflow-profile` in `solution_manager/cli.py`,
  `initialize_workflow` in `solution_manager/core/workflow.py`,
  `Tools/SentinelToXDRMigration/agent-workflows/end-to-end-migration.md`, and
  agent adapters (`AGENTS.md`, `CLAUDE.md`, `.github`, `.claude`, `.cursor`, and
  `.windsurf`) from `authoring` to `qualification`, preserving
  `--workflow-profile authoring` as an explicit offline/ISV fallback when no
  live lab is available.

## Candidate follow-ups

- [x] **Flip default workflow profile from `authoring` to `qualification` after live
  lab sign-off.** Completed: `workflow-init`, `initialize_workflow`, canonical
  workflow docs, and all agent adapters now default to `qualification` with
  `authoring` preserved as an explicit offline/ISV fallback.

Any future environment write remains separately gated by explicit approval
immediately before the exact operation. No cloud action is authorized by this
roadmap.
