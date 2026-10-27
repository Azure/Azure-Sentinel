# Qualification checklist

General solution qualification, not a migration prerequisite for native content.
Apply the [result, exception and safety contract](README.md#results-author-evidence-and-rollups).
Every live action requires the selected non-production target and its own
approved scope. A definition or exception is not execution permission.

## QUAL-00 — Validation checklist passed

This is the first check and a mandatory, non-waivable prerequisite. A partial
Validation rollup permits only a conditional Qualification rollup.

```yaml check-definition
id: QUAL-00
checklist: qualification
contentType: all
title: Validation checklist passed
originalCriterion: Validation checklist rollup must be Validated or Partially Validated before Qualification can pass.
applicability: Every Qualification run, including native content and active migration overlays.
category: validation
howPerformed: Verify the current Validation rollup, check-instance results, acknowledged exclusions and exceptions against the same head/input hashes; include active migration validation checks.
expectedEvidence: [Validation rollup artifact ref, head and input hashes, check result inventory, exclusion and exception decision refs, safety gate results]
passCriteria: Current Validation rollup is Validated or Partially Validated with all safety gates passed. Partially Validated forces Conditionally Qualified downstream. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; fix the upstream rollup instead.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned PR check runner rollup evaluator
```

## E2E-G01 — No simulated fallbacks in Qualification mode

Non-waivable. Missing real callbacks, dry-run stubs and locally fabricated
successes cannot establish deployment, ingestion, query, alert or UI proof.

```yaml check-definition
id: E2E-G01
checklist: qualification
contentType: all
title: No simulated fallbacks in Qualification mode
originalCriterion: Verify real Azure, KQL and browser providers were used and block dry-run stubs.
applicability: Every live Qualification check and every imported-live evidence artifact.
category: validation
howPerformed: Verify real provider readiness for every applicable live step and actual provider/collector identity, target, request/query hash, response/capture references and timestamps for every live claim; reject simulation, missing providers and self-reported success booleans without verifiable observations.
expectedEvidence: [provider and collector identity, live request/response or browser capture refs, target binding, input/query hashes, execution timestamps, evidence mode]
passCriteria: Applicable live steps have verified real providers and all live claims have current verifiable real-provider evidence; imported-live evidence includes collection provenance. Functional waivers make no live claim and cannot excuse missing providers or conceal attempted simulation. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; simulation never yields Qualified or Conditionally Qualified.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned real-provider evidence gate around runtime, ARM, DCR, alert and browser adapters
```

## TK-G02 — Locked target scope and identity

Non-waivable. A workspace in one surface does not establish another surface's
tenant or data availability.

```yaml check-definition
id: TK-G02
checklist: qualification
contentType: all
title: Locked Non-production Target Verification
originalCriterion: Bind the selected tenant, subscription, workspace and exact resource identities and reject scope mismatches.
applicability: Every lab read, deployment, injection, alert action and browser session.
category: validation
howPerformed: Compare persisted target, authenticated identity, request resource IDs and observed portal/provider identities immediately before dispatch and when accepting results.
expectedEvidence: [private target config ref, approved resource scope, authenticated identity binding, expected and observed IDs, target verification receipt]
passCriteria: Every operation and observation matches the approved non-production scope. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; wrong or unknown targets block execution and successful rollups.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.core.target_context, runtime and workbook_preflight; planned cross-provider scope adapter
```

## TK-G03 — Explicit operation authorization

Non-waivable. Review acceptance and author exceptions never grant permissions.

```yaml check-definition
id: TK-G03
checklist: qualification
contentType: all
title: Explicit Exact-scope Authorization
originalCriterion: Require separate current approvals for reads, browser execution, deployment, ingestion, activation and cleanup.
applicability: Every Qualification action; re-evaluate changed or revoked scope.
category: validation
howPerformed: Verify affirmative actor/reference-bound consent for the exact operation and target, freshness and revocation; require immediate write approval where the canonical route requires it.
expectedEvidence: [operation plan ref and hash, approval actor/reference, allowed resources and operations, revocation state, immediate confirmation receipt when required]
passCriteria: Applicable current authorization exists before dispatch and remains valid. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; author justification cannot authorize a missing read/write scope.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.runtime_consent, deployment_planning and workbook preflight/UI consent gates
```

## TK-G04 — Effective permissions and readiness

Non-waivable. Cached authentication and declarations are not effective access.

```yaml check-definition
id: TK-G04
checklist: qualification
contentType: all
title: Effective Access and Provider Readiness
originalCriterion: Inspect effective permissions, applicable roles and deny assignments separately from approval.
applicability: Each selected provider operation, including conditional DCR, DCE or table creation.
category: qualification
howPerformed: Use approved read preflight to inspect actual access and provider contracts; report query, deployment, ingestion and conditional provisioning permissions separately.
expectedEvidence: [preflight response refs, principal/target binding, role and deny observations, per-operation permission results, unresolved provider contract findings]
passCriteria: Required access and provider readiness are established for each action. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; denied or unknown access blocks that action.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.graph_readiness, dcr_readiness and workbook_preflight
```

## QUAL-MOCK-01 — Mock scenario semantic adequacy

Validation checks files and schemas; this check establishes whether fixtures
exercise each packaged detection and workbook query meaningfully.

```yaml check-definition
id: QUAL-MOCK-01
checklist: qualification
contentType: all
title: Mock Scenario Semantic Qualification
originalCriterion: Sample values support all data types and scenarios and represent the product-appliance data experience.
applicability: All packaged Sentinel ARs, XDR CDs, Sentinel workbooks and XDR workbooks.
category: qualification
howPerformed: Review scenario-to-item/query mappings, joins, thresholds, sequences, time windows, baselines, parameter states and positive/benign controls; define expected results before execution.
expectedEvidence: [fixture manifest and hashes, item/query coverage map, expected malicious and benign keys, parameter/time bindings, semantic review decisions and evidence refs]
passCriteria: Each packaged item has a defensible scenario and independently reviewed expected behavior. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified, not proven semantic coverage.
sourceChecklist: master-excel
automationStatus: agent-qualified
responsible: Mock-data qualification agent with content owner review; existing scenario generation is an input, not the oracle
```

## TK-Q08 — DCR stream and destination compatibility

Do not confuse public table schemas with supported writable input streams.

```yaml check-definition
id: TK-Q08
checklist: qualification
contentType: all
title: DCR Ingestion Contract Compatibility
originalCriterion: Prove the exact stream, transform, destination schema and endpoint are compatible with the shared fixture.
applicability: Every fixture/table requiring live DCR injection.
category: qualification
howPerformed: Inspect deployed approved DCR resources and public Custom-* input streams, transformKql, table schema and endpoint; use a solution DCR only when compatibility is proven.
expectedEvidence: [DCR resource and immutable ID refs, input stream, transform and destination schema, endpoint ref, resource/contract fingerprints, fixture schema comparison]
passCriteria: The real ingestion contract supports the fixture and target without modifying an unrelated connector or substituting a custom lookalike native table. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; scope/access/privacy gates remain non-waivable.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.dcr_readiness and approved registered-contract resolver; solution-first automatic discovery remains planned
```

## E2E-Q01 — Live DCR injection and table landing

Require marker-bound data visibility, not just ingestion acceptance or a
background table count. Verify each relevant query surface independently.

```yaml check-definition
id: E2E-Q01
checklist: qualification
contentType: all
title: Live DCR Mock Injection and Table Landing Verification
originalCriterion: Mock data is injected into the live lab workspace via DCR and independently verified in the destination tables.
applicability: All approved fixtures for packaged detections and workbooks; migration is not required.
category: qualification
howPerformed: Submit each approved shared payload exactly once through a verified real DCR route; query exact scenario markers and expected row keys/types on required Sentinel and XDR surfaces within bounded visibility windows.
expectedEvidence: [payload and contract hashes, approved scope ref, real ingestion response ref, submission/deduplication ledger, marker-filtered query text and hashes, expected and observed row keys/counts, provider/target/timestamps]
passCriteria: Ingestion is accepted and complete expected marked data is visible in each required surface. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; no actual injection claim follows and E2E-G01/TK-G02/TK-G03/TK-G07 cannot be waived.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Approved AzureMonitorLogsIngestion route and planned live marker-bound landing adapter; generic mock_data fallback is not evidence
```

## QUAL-RUNTIME-01 — Every packaged query runs

Checklist 2 requires regular rules to be tested when XDR exists. This general
check also covers source-only/native content and non-detection queries.

```yaml check-definition
id: QUAL-RUNTIME-01
checklist: qualification
contentType: all
title: Packaged Content Runtime Query Validation
originalCriterion: Test regular rules when the PR contains XDR detections; installed hunting and connector queries run without errors.
applicability: Every packaged AR/CD and applicable hunting, parser, connector and workbook query, including impacted dependencies.
category: qualification
howPerformed: Execute exact persisted queries with approved parameter bindings against their actual intended providers; enumerate every required query, record complete responses and compare actual output schemas with required entity/custom-detail, projection and visualization bindings.
expectedEvidence: [packaged query inventory, query hashes and bindings, provider/target refs, execution response files, schemas, row counts, per-query errors]
passCriteria: Every applicable exact query executes successfully with complete current evidence; zero rows establish execution only, not E2E-Q02 or E2E-Q04. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; safety gates remain mandatory.
sourceChecklist: pr-checklist-2-docx
automationStatus: automated
responsible: solution_manager.qualification.runtime and planned general content query adapters
```

## E2E-Q02 — Every packaged detection actually fires

Require individual firing proof for native/unpaired detections. Migration parity
is an additional overlay, never a reason to omit unpaired content.

```yaml check-definition
id: E2E-Q02
checklist: qualification
contentType: all
title: Every Packaged Sentinel and XDR Detection Fires
originalCriterion: Every packaged Sentinel AR and XDR CD starts disabled, is enabled, fires at least one scenario-correlated alert from injected mock data and is returned to disabled.
applicability: Every packaged Sentinel Analytic Rule and Defender XDR Custom Detection.
category: qualification
howPerformed: Under TK-Q11 lifecycle control, activate the exact approved detection identities and coordinate fixture timing; capture real expected alerts within schedule-aware windows and correlate them to injected scenario keys.
expectedEvidence: [packaged detection IDs, TK-Q11 state/approval receipts, fixture/injection refs, observation window, actual alert IDs and raw capture refs, scenario match keys, final disabled readback]
passCriteria: Every packaged detection produces at least one expected scenario-correlated alert and TK-Q11 passes. Firing FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified without claiming it fired; activation safety and disabled-state cleanup cannot be waived.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned all-detection firing adapter reusing solution_manager.qualification.alert_parity lifecycle and real alert collectors
```

## TK-Q11 — Controlled activation and safe completion

Non-waivable safety gate. Reuse E2E-Q02 evidence without duplicating activation.

```yaml check-definition
id: TK-Q11
checklist: qualification
contentType: all
title: Controlled Alert Lifecycle and Disabled-state Cleanup
originalCriterion: Verify disabled starting state, enable only reviewed detections and disable every test detection after success or failure.
applicability: Every packaged detection participating in live firing or migration parity.
category: qualification
howPerformed: Verify exact identities and initial disabled state, scoped activation consent, controlled enablement and bounded observation; execute approved complete/abort cleanup and independently read back disabled state.
expectedEvidence: [initial state captures, activation/cleanup approvals, exact detection IDs, enablement receipts, completion or abort record, final disabled-state response refs]
passCriteria: All test detections start disabled, activation stays within scope and all return to disabled with real readback. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; incomplete safe cleanup blocks a successful rollup.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.alert_parity complete/abort and planned native/unpaired detection lifecycle adapter
```

## E2E-Q04 — Every workbook query returns injected scenario data

Positive row count is necessary but insufficient. A one-row count of zero is
not useful scenario data. Keep intended empty negative tests separate.

```yaml check-definition
id: E2E-Q04
checklist: qualification
contentType: workbooks
title: Every Workbook Query Returns Injected Data
originalCriterion: Every Workbook query executes against injected data and returns rowCount greater than zero with non-zero scenario values.
applicability: Every runnable query in every packaged Sentinel or XDR workbook, including nested, hidden, picker and parameter queries.
category: qualification
howPerformed: Execute exact authored queries with reviewed parameter/time bindings against real providers after verified injection; compare schema/results with expected scenario values and demonstrate injected-data contribution.
expectedEvidence: [complete workbook/query inventory, query and binding hashes, fixture and landing refs, provider responses, rowCount, aggregate/scenario values, expected versus observed results]
passCriteria: Each query has a complete successful response with rowCount greater than zero and meaningful non-zero expected scenario values, not a zero-count aggregate or unrelated rows. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; non-ingestible providers are disclosed, not silently passed.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned workbook live-data adapter reusing workbook_qualification execution contracts; offline fixture harnesses do not satisfy this check
```

## TK-G06 — Approved browser plan and session

Non-waivable. Portal traversal is not authorization to configure or save content.

```yaml check-definition
id: TK-G06
checklist: qualification
contentType: all
title: Approved Browser Scope and Session Verification
originalCriterion: Use reviewed exact URLs, selectors, expected identities, bounded actions and network scope without Save/Edit or automatic sign-in.
applicability: All UI-agent checks for detections, workbooks, connectors and their assets.
category: validation
howPerformed: Validate browser plan, private session binding, observed tenant/content identities, navigation and read-query requests, timeout bounds and prohibited controls before and during traversal.
expectedEvidence: [reviewed browser plan/hash, approval ref, private session hash reference, identity observations, allowed actions/requests, prohibited-control findings]
passCriteria: Browser activity remains in the authorized target and read/observe interaction scope with no unapproved writes. FAIL, SKIPPED or BLOCKED cannot become WAIVED_WITH_AUTHOR_EVIDENCE; this is not a browser-wide no-write sandbox guarantee.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.workbook_browser and planned cross-content browser-plan adapter
```

## E2E-Q05 — Portal traversal of all user-facing content

Covers Master solution UI and Checklist 2 Basics/Manage terminology. Enumerate
required states rather than claiming an unbounded crawl is complete.

```yaml check-definition
id: E2E-Q05
checklist: qualification
contentType: all
title: UI Agent Traverses All User-facing Portal Content
originalCriterion: Traverse Detections, Workbooks and Data Connectors; Basics displays correct counts and Manage lists regular rules and XDR rules.
applicability: Every packaged detection, workbook and data connector and associated solution/package UI.
category: qualification
howPerformed: Use a reviewed content-to-view/state manifest to visit list/detail pages, Basics, Manage, workbook tabs/conditional sections and connector instructions/next steps; wait for lazy content and reconcile inspected versus required states.
expectedEvidence: [portal view/state inventory, exact content IDs and target, expected versus observed Basics counts and Manage entries, per-view screenshots/DOM refs, loading/query/JS errors, missing-view list]
passCriteria: Every required user-facing view/state is visited and correctly displays expected content without unresolved loading or errors. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; TK-G06 and other safety gates cannot be waived.
sourceChecklist: user-e2e-requirement
automationStatus: agent-qualified
responsible: Planned cross-content portal UI agent reusing reviewed workbook_browser contracts
```

## E2E-Q06 — Images, logos, diagrams and visualization rendering

Use element-appropriate assertions. `naturalWidth` applies to image elements,
not inline SVG or canvas; HTTP status applies to fetched assets.

```yaml check-definition
id: E2E-Q06
checklist: qualification
contentType: all
title: UI Images Logos SVG Diagrams and Visualizations Render
originalCriterion: All images, logos, SVG diagrams and workbook visualizations render properly with naturalWidth greater than zero, HTTP 200 and zero broken assets.
applicability: All assets and visualizations in the E2E-Q05 view/state inventory, including lazy-loaded and conditional content.
category: qualification
howPerformed: For image elements require successful decode and naturalWidth greater than zero; verify fetched assets return HTTP 200 using a reviewed cache-aware capture; inspect inline SVG/canvas bounds and rendered content plus workbook visualizations and screenshots.
expectedEvidence: [asset-to-view inventory, asset URLs or inline element IDs, HTTP status/response refs for fetched assets, image decode and naturalWidth observations, SVG/canvas render assertions, screenshots, broken asset count]
passCriteria: All assets render as intended with zero broken assets; image elements have positive naturalWidth, fetched assets have evidenced HTTP 200, and inline diagrams/visualizations have positive render proof. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; safety gates remain mandatory.
sourceChecklist: user-e2e-requirement
automationStatus: agent-qualified
responsible: Planned UI asset/rendering agent and deterministic browser asset probes
```

## TK-Q06 — Workbook interactions

All seven existing workbook interaction kinds remain required, independently of
whether a screenshot looks correct.

```yaml check-definition
id: TK-Q06
checklist: qualification
contentType: workbooks
title: Workbook Picker Filter Navigation and Layout Qualification
originalCriterion: Verify pickers, dependent refresh, filters, drill-down, reload, layout and conditional visibility with reviewed expectations.
applicability: Every packaged interactive Sentinel or XDR workbook; static-only non-applicability needs explicit evidence.
category: qualification
howPerformed: Execute reviewed non-edit browser steps for each applicable interaction kind and compare DOM values, layout and dependent results with predetermined expectations.
expectedEvidence: [workbook identity and hash, seven-kind coverage inventory, reviewed step plan, expected and actual assertions, screenshots and browser trace refs]
passCriteria: Every applicable reviewed interaction passes without query/JS errors or prohibited actions. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; browser authorization cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: agent-qualified
responsible: solution_manager.qualification.workbook_qualification and workbook_browser; Sentinel/general adapters planned
```

## TK-Q07 — Installation, registration and managed updates

Template success is not proof of installed content, provenance or update behavior.

```yaml check-definition
id: TK-Q07
checklist: qualification
contentType: solution-package
title: Live Installation Registration and Managed Update Verification
originalCriterion: Verify independent installation and registration/provenance readback and repeat-install/update contracts.
applicability: Approved live package acceptance, including packaged content and managed XDR workbook/detection updates.
category: qualification
howPerformed: Perform approved installation and exact resource readback; compare content/package identity/version and selected inventory; verify same-ID managed updates without touching separate personal copies.
expectedEvidence: [candidate/package refs, deployment response, independent installed resource and registration readback, identity/version comparisons, repeat-install/update receipts, personal-copy exclusion evidence]
passCriteria: Selected content is installed and registered as contracted and applicable managed-update proof passes. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; unverified provider authentication/write scope still blocks dispatch.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.workbook_validation, qualification.arm_acceptance and deployment adapters
```

## TK-Q04 — Live dependency metadata

Input metadata is neither output lineage nor connector installation evidence.

```yaml check-definition
id: TK-Q04
checklist: qualification
contentType: all
title: Live Dependency Metadata Reconciliation
originalCriterion: Compare exact-query live input metadata with declared workloads, connectors and data types.
applicability: Content with unresolved or changed data dependencies where approved live discovery is selected.
category: qualification
howPerformed: Capture exact-query input metadata on the intended surface with reviewed bindings; compare declarations, retain partial failures and distinguish documented conservative scanner fallback from observed metadata.
expectedEvidence: [query hash and parameter bindings, provider/target ref, raw input metadata, declared versus observed dependencies, fallback classification, review decision refs]
passCriteria: Applicable dependencies are reconciled with current complete evidence and explicit decisions. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; privacy and read consent remain non-waivable.
sourceChecklist: toolkit-contract
automationStatus: agent-qualified
responsible: solution_manager.authoring.dependencies, workbook_dependencies and dependency-helper agent
```

## QUAL-URL-01 — Open short URLs and verify expected destinations

Cover mainTemplate and createUiDefinition; the existing hyperlink script's
Package exclusions must not hide these checks.

```yaml check-definition
id: QUAL-URL-01
checklist: qualification
contentType: all
title: Short URL and Expected Destination Qualification
originalCriterion: Open or hit updated short URLs and verify that they return the expected result.
applicability: Short URLs in package files and changed content links, including links affected by moved/deleted targets.
category: qualification
howPerformed: Follow approved bounded redirects, capture final response/destination and compare content with the expected product, documentation or deployment artifact; do not deploy by following a button.
expectedEvidence: [source URL inventory and file locations, old/new URLs, redirect chains, HTTP outcomes, expected and observed destination identity/content, capture refs]
passCriteria: Required links resolve to the correct accessible content, not merely an HTTP success or sign-in/error page. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; unsafe navigation or credential disclosure cannot be waived.
sourceChecklist: pr-checklist-2-docx
automationStatus: agent-qualified
responsible: Planned package-inclusive URL qualification adapter and content reviewer
```

## QUAL-RULE-01 — Rule and hunt semantic review

Syntax, successful execution and firing are separate from detecting the intended
behavior. This check does not require a migration.

```yaml check-definition
id: QUAL-RULE-01
checklist: qualification
contentType: all
title: Analytic Rule and Hunting Query Semantic Review
originalCriterion: Description matches query intent; frequency, period, trigger and threshold match the expected outcome and entity mappings are meaningful.
applicability: Packaged or changed analytic rules, XDR detections and hunting queries; apply only kind-appropriate criteria.
category: human-review
howPerformed: Review attacker behavior, telemetry, query operators/case handling, aggregation/projected context, timing, MITRE meaning, entity coverage and suitability as a rule or hunt using runtime/scenario evidence.
expectedEvidence: [content and query refs, expected behavior, positive/negative results, timing/threshold rationale, MITRE/entity rationale, named reviewer decision]
passCriteria: The reviewer confirms defensible behavior, appropriate kind-specific settings and understandable context. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; this does not erase technical or safety failures.
sourceChecklist: master-excel
automationStatus: human-review
responsible: Detection/hunting content reviewer assisted by a bounded qualification agent
```

## QUAL-TI-01 — Threat intelligence matching semantics

Cross-apply the five TI Matching criteria; retain historical "Not in TCS scope"
as an ownership marker, not an automatic exclusion.

```yaml check-definition
id: QUAL-TI-01
checklist: qualification
contentType: all
title: Threat Intelligence Matching Qualification
originalCriterion: Filter inactive indicators, use applicable IP indicators and fields, and select the latest indicator before checking active state.
applicability: Rules, hunts, parsers, workbooks or playbooks using threat intelligence matching, including current equivalents of historical TI tables.
category: qualification
howPerformed: Inspect query ordering and indicator semantics and test active/inactive, duplicate/latest, non-IP and alternate relevant IP-field scenarios against the current TI contract.
expectedEvidence: [TI query locations, current table/schema contract, scenario fixtures, expected versus actual indicator matches, reviewer rationale]
passCriteria: Applicable TI scenarios and reviewed matching semantics pass without treating stale indicators as current. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; scope/privacy gates remain mandatory.
sourceChecklist: master-excel
automationStatus: agent-qualified
responsible: TI content reviewer and planned scenario qualification adapter
```

## QUAL-PARSER-01 — Parser deployment, output and ASIM mapping

Test actual output fields and filter behavior, not merely function creation.

```yaml check-definition
id: QUAL-PARSER-01
checklist: qualification
contentType: parsers
title: Parser Runtime and ASIM Mapping Qualification
originalCriterion: Parser deploys, runs on sample data and returns extended fields; relevant source fields map correctly to ASIM.
applicability: Packaged or changed parsers and affected consumers, including parameterized ASIM parsers.
category: qualification
howPerformed: Use approved installation/read routes, execute representative samples and filter cases, and compare returned schema/values with reviewed generic or ASIM expectations.
expectedEvidence: [installed function identity, parser/sample hashes, query and filter cases, expected versus actual fields/types/values, deployment and runtime response refs]
passCriteria: Applicable parser deployment, outputs and filter/mapping assertions pass. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; authorization and real-provider requirements cannot be waived.
sourceChecklist: master-excel
automationStatus: agent-qualified
responsible: Existing ASIM validation tools and planned general parser live adapter
```

## QUAL-DC-01 — Connector runtime and operational behavior

Successful invocation alone does not establish correct paging or complete data.

```yaml check-definition
id: QUAL-DC-01
checklist: qualification
contentType: data-connectors
title: Data Connector Operational Qualification
originalCriterion: Connector queries work; Azure Function deployment and execution are checked, including authentication, filtering, pagination, batching and invocation logs.
applicability: Packaged connectors and changed connector execution/deployment files.
category: qualification
howPerformed: Under approved scope verify connector visibility and runtime queries, applicable function/custom-connector installation, supported authentication and representative ingestion behavior; inspect full logs and document every warning/error.
expectedEvidence: [connector and function IDs, approved scenario, deployment/invocation response refs, expected and observed pages/records, query results, complete log findings]
passCriteria: Applicable connector behaviors and expected records are verified with no unexplained failures; a historical 403 exception is not a blanket access waiver. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified.
sourceChecklist: master-excel
automationStatus: agent-qualified
responsible: Planned connector/function qualification adapter and connector reviewer
```

## QUAL-PLAYBOOK-01 — Playbook deployment and user experience

Do not trigger external actions without separate scenario-specific authorization.

```yaml check-definition
id: QUAL-PLAYBOOK-01
checklist: qualification
contentType: playbooks
title: Playbook Deployment and Functional Qualification
originalCriterion: Playbooks deploy successfully and appear in Template gallery, Active playbooks, Manual trigger and Automation rule experiences.
applicability: Packaged or changed playbooks and their connection resources.
category: qualification
howPerformed: Verify approved deployment, connection resources and relevant UI surfaces; exercise explicitly approved bounded scenarios and assess errors, authentication setup and Azure/Gov deployment links where supported.
expectedEvidence: [template and connection identities, deployment/readback refs, gallery/trigger screenshots, approved action scope, scenario outcomes, connection and error findings]
passCriteria: Applicable deployment, visibility and functional scenarios pass with authorized connections/actions. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; authorization/privacy gates remain mandatory.
sourceChecklist: master-excel
automationStatus: agent-qualified
responsible: Planned playbook qualification adapter and playbook reviewer
```

## QUAL-NOTEBOOK-01 — Notebook quality, execution and exceptions

MSTIC approvals for relative data/external code remain explicit human decisions.

```yaml check-definition
id: QUAL-NOTEBOOK-01
checklist: qualification
contentType: notebooks
title: Notebook Usability Runtime and MSTIC Review
originalCriterion: Notebook purpose and logic are understandable, handles null results, uses existing capabilities and is tested on AML Notebook VM.
applicability: Packaged or changed notebooks and referenced data/code/APIs.
category: human-review
howPerformed: Review explanations, naming, readable data presentation, msticpy reuse, configuration and API onboarding; inspect approved AML or explicitly reviewed equivalent execution evidence and obtain applicable MSTIC external-file sign-off.
expectedEvidence: [notebook/cell refs, approved execution environment, positive/null-result outputs, dependency/configuration review, privacy check ref, MSTIC decision refs where required]
passCriteria: Named reviewer accepts usability and applicable runtime evidence, with required external-code/data approvals. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; privacy or execution authorization cannot be waived.
sourceChecklist: master-excel
automationStatus: human-review
responsible: Notebook/MSTIC reviewer assisted by a bounded notebook qualification agent
```

## QUAL-TEXT-01 — Descriptions, branding and visual usefulness

Preserve source requirements such as meaningful descriptions, four workbook
charts and 75px logos; explicitly adjudicate legacy/current policy differences.

```yaml check-definition
id: QUAL-TEXT-01
checklist: qualification
contentType: all
title: Content Explanation and Presentation Review
originalCriterion: Descriptions are meaningful and grammatically correct, provider/appliance names exist, and images and workbook content are useful.
applicability: Changed user-facing descriptions, instructions, previews, charts, logos and product references.
category: human-review
howPerformed: Review product identity, supported technology descriptions, prerequisites, Preview labels, grammar, appropriate visualizations and legibility using current documentation and UI evidence.
expectedEvidence: [text/asset source locations, product/reference evidence, expected and observed presentation, chart inventory, 75px logo capture where applicable, reviewer decision]
passCriteria: Reviewer confirms clear accurate content and resolves applicable legacy presentation criteria explicitly. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; privacy and source access restrictions remain non-waivable.
sourceChecklist: master-excel
automationStatus: human-review
responsible: Content review owner assisted by text and UI qualification agents
```

## QUAL-RELEASE-01 — Ownership, publication and removal decisions

Post-merge checks retain their lifecycle phase; do not claim them completed
before publication. No publishing or short-link creation is authorized here.

```yaml check-definition
id: QUAL-RELEASE-01
checklist: qualification
contentType: solution-package
title: Ownership Publication and Removal Review
originalCriterion: Confirm solution ownership, Partner Center listing requirements, post-merge gallery/shortlinks and Connector team approval before removing a Function App connector.
applicability: Relevant new/update releases, Microsoft-supported offer changes, connector removals, ownership changes and post-merge publication verification.
category: human-review
howPerformed: Verify authorized owner decisions, deletion/conflict-resolution impact, offer identity, Sentinel keyword/CSP settings and listing-update evidence; track gallery and short-link follow-up at the correct release phase.
expectedEvidence: [release phase, ownership and team approval refs, deletion impact, Partner Center identity/settings evidence, listing-update receipt, post-merge gallery/link observations or pending obligations]
passCriteria: Applicable phase-specific publication and team decisions are evidenced; future obligations remain visible and cannot be claimed passed. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; actual operation authorization cannot be waived.
sourceChecklist: master-excel
automationStatus: human-review
responsible: Solution owner, Connector team, content review team and release manager
```

## E2E-V04 — Qualification coverage and final evidence reconciliation

The full source inventory remains visible even when the packaged subset is
smaller. Conditional outcomes must never be presented as full coverage.

```yaml check-definition
id: E2E-V04
checklist: qualification
contentType: all
title: Qualification Coverage and Evidence Reconciliation
originalCriterion: Reconcile every required item and check against real evidence; missing, simulated or skipped results are not successful live checks.
applicability: Final rollup for every Qualification run, including active migration checks and newly captured privacy-sensitive evidence.
category: validation
howPerformed: Reconcile packaged detection, workbook/query, portal-view and asset denominators with check instances; recheck safety/privacy, freshness, cleanup and exception records; preserve excluded source items and prior outcomes.
expectedEvidence: [full and packaged inventories, expected/tested/passed/missing identities, all check result refs, exception manifest ref, safety and cleanup receipts, final sanitized evidence index]
passCriteria: Qualified requires Validated and every applicable check PASS with no exclusions/waivers. Valid author evidence for non-safety FAIL or SKIPPED may yield WAIVED_WITH_AUTHOR_EVIDENCE and Conditionally Qualified; Partially Validated also caps the rollup. Missing safety proof, QUAL-00 failure or unresolved blocks cannot be waived.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned PR check runner rollup/evidence reconciliation adapter
```
