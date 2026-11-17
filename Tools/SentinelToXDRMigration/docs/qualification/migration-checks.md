# Sentinel-to-Defender-XDR migration overlay

Activate only for a PR migrating Sentinel content to paired `XDR Detections/`
or `XDR Workbooks/`, including changes to an existing migration pair.
Native XDR content or folder presence alone does not activate this overlay.
Apply the [scope and rollup contract](README.md). Validate pairing from
provenance and PR intent; ambiguity is unresolved rather than silently skipped.

Static `category: validation` checks contribute to the Validation rollup.
Live `category: qualification` checks contribute to Qualification only when
that profile is explicitly selected. Offline authoring never claims live
parity. General validation, privacy, authorization and real-provider gates
remain mandatory; this overlay does not duplicate their execution.

## TK-V01 — Complete migration source inventory

Keep the full source denominator separate from the acknowledged packaged scope.

```yaml check-definition
id: TK-V01
checklist: migration
contentType: all
title: Complete Migration Inventory and Pairing
originalCriterion: Account for every source rule/workbook, target artifact, duplicate or ambiguous identity and unresolved conversion outcome.
applicability: Active Sentinel-to-XDR migration; inventory every source and target in the declared migration scope.
category: validation
howPerformed: Reconcile recursive source inventory and hashes with conversion manifests and target provenance; retain unmigrated/failed/excluded items and reject pairing by list position or name guess.
expectedEvidence: [source and target inventories/hashes, conversion manifest ref, explicit pair mappings, duplicate/ambiguity findings, excluded and unresolved outcomes]
passCriteria: Migration inventory is complete and every pair is defensible without hidden failures or a reduced denominator. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; scope safety remains non-waivable.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.authoring_contract, migration manifests and planned PR migration detector
```

## TK-V02 — Source-derived XDR identity

Apply `xdr-<GUID>` only to Sentinel-derived detections, not native XDR IDs.

```yaml check-definition
id: TK-V02
checklist: migration
contentType: xdr-detections
title: Sentinel-derived XDR Identity Validation
originalCriterion: Sentinel-derived properties.id is the canonical xdr- prefix plus the source Sentinel GUID with complete source provenance.
applicability: Sentinel AR to XDR CD pairs in an active migration.
category: validation
howPerformed: Validate source GUID, Graph-compatible target identity, canonical xdr-<GUID> relationship, source path/platform/kind and exact source/query provenance hashes.
expectedEvidence: [source and target IDs, provenance field locations, expected canonical ID, observed ID, source/query hash comparisons]
passCriteria: Each migrated CD has the required source-derived identity and current provenance. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; no deployed identity change is authorized.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.migration.converter.validate_document and XDR schema validation
```

## TK-V03 — NRT, lookback and schedule transformation

Preserve the distinction between supported transformation and proven behavior.

```yaml check-definition
id: TK-V03
checklist: migration
contentType: xdr-detections
title: NRT and Schedule Migration Contract
originalCriterion: Validate Continuous PT0S eligibility, supported cosmetic summarize rewrites and documented PT1H fallback/lookback contracts.
applicability: Migrated detection pairs, especially source NRT or changed frequency/lookback.
category: validation
howPerformed: Inspect source kind and exact transformed query; validate eligible row-level PT0S, supported cosmetic summarize rewrite and recorded PT1H fallback for incompatible behavioral shapes; verify PT4H or other applicable target lookback evidence.
expectedEvidence: [source kind/frequency/period, target frequency/lookback, original and rewritten query hashes, eligibility findings, event-time window provenance, review decision refs]
passCriteria: Transformation follows the supported contract with timing changes and unresolved assumptions visible; no parity is inferred. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated without changing deployment gates.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.migration.converter NRT eligibility, cosmetic summarize rewrite and schedule validation
```

## TK-V04 — XDR entity binding integrity

Entity labels alone do not establish usable XDR evidence bindings.

```yaml check-definition
id: TK-V04
checklist: migration
contentType: xdr-detections
title: Migrated XDR Entity Binding Integrity
originalCriterion: Produce supported asset mappings and require genuine content hash columns for file/process bindings.
applicability: Migrated Sentinel AR to XDR CD entity mappings.
category: validation
howPerformed: Check required Host/Account/Mailbox/IP mappings, identifier translation and output bindings; reject filenames or synthetic/non-content hashes substituted for required SHA1/SHA256 values; preserve supplemental context explicitly.
expectedEvidence: [source and target mapping locations, query projection/schema refs, hash-column provenance, expected and observed entity bindings, unresolved review findings]
passCriteria: Entity mappings satisfy the supported XDR contract without fabricated bindings or silent context loss. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; this does not prove live entity parity.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.migration.converter entity mapping and hash validation
```

## TK-V05 — Custom-detail preservation and binding

Static limits and actual output-schema verification are separate checks.

```yaml check-definition
id: TK-V05
checklist: migration
contentType: xdr-detections
title: Migrated Custom-detail Integrity
originalCriterion: Preserve custom-detail bindings, reject conflicts and missing output columns, and retain documented limits and runtime binding requirements.
applicability: Migrated detection pairs with original or supplemental custom details.
category: validation
howPerformed: Compare source/target key-to-column bindings and final projections, check supported pair/key-size limits and record unresolved output bindings for TK-Q02; never silently truncate or overwrite.
expectedEvidence: [source/target customDetails, final query hash and projections, conflict/missing-column findings, limit measurements, runtime verification requirements]
passCriteria: Custom-detail preservation and static contracts pass with required runtime binding checks identified. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; schema alone does not verify runtime value size.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.migration.converter custom-detail conversion/validation and authoring.columns
```

## TK-V08 — Exact migration package selection

An explicit empty selection stays empty; excluded files remain visible.

```yaml check-definition
id: TK-V08
checklist: migration
contentType: solution-package
title: Migration Package Selection Integrity
originalCriterion: Package only explicit reviewed selections and prevent rescanning folders from reintroducing excluded detections.
applicability: Active migration with explicit full or partial AR/CD or workbook package selection.
category: validation
howPerformed: Compare current selection plan and apply receipt with source data arrays, current artifacts and exact package/ZIP identities; preserve excluded artifacts and original failure evidence.
expectedEvidence: [selection plan/hash, author decision and apply receipt refs, source data arrays, included/excluded identities, package and ZIP comparisons]
passCriteria: Package matches the explicit current selection with no omitted selection evidence or reintroduced exclusions. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; existing package execution gates are unchanged.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.packaging.packaging_selection and packaging verification
```

## TK-V09 — Migration coverage and partial-publication contract

This toolkit-specific threshold is not the general E2E-V01 inventory rule.

```yaml check-definition
id: TK-V09
checklist: migration
contentType: all
title: Migration Coverage and Partial Publication Accounting
originalCriterion: Measure eligible migrated source IDs against the complete original inventory and do not claim selected-subset success as full-inventory success.
applicability: Active migration; apply the strict over-50-percent threshold only to the existing partial-detection publication route, not workbook-only or native solutions.
category: validation
howPerformed: Use unique validated source IDs and complete source denominator; verify source/target evidence eligibility and route-specific threshold; report failed, excluded and untested identities.
expectedEvidence: [full denominator and source IDs, eligible numerator and evidence refs, selected workflow route, threshold computation, excluded/failed/untested inventory]
passCriteria: Applicable route-specific coverage contract is satisfied without inflated numerator or reduced denominator. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated in this review; it does not authorize a package blocked by existing toolkit gates.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.authoring_contract and solution_manager.packaging.packaging_selection
```

## MIG-WB-01 — Workbook query transformation and provenance

Preserved non-Log-Analytics providers are not silently treated as migrated KQL.

```yaml check-definition
id: MIG-WB-01
checklist: migration
contentType: xdr-workbooks
title: Workbook Migration Query and Provenance Integrity
originalCriterion: Bind source and converted workbook/query identities and preserve reviewed provider, parameter and function semantics.
applicability: Sentinel workbook to XDR workbook pairs in an active migration.
category: validation
howPerformed: Reconcile every query/picker pointer and source hash with converted or preserved-provider outcomes; validate reviewed dependencies/functions and public-workbook provenance while keeping private receipts outside content.
expectedEvidence: [source/target workbook hashes, query/picker pointer map, provider dispositions, query contracts, dependency decisions, private/public artifact refs]
passCriteria: Every source query/picker is accounted for and target contracts and reviewed provenance are current. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; TK-G07 privacy cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.migration.workbooks and authoring workbook dependency/publication modules
```

## TK-Q01 — Dual-surface exact runtime KQL

Execute both sides on their actual surfaces; one side cannot stand in for both.

```yaml check-definition
id: TK-Q01
checklist: migration
contentType: all
title: Sentinel LA and XDR Advanced Hunting Runtime Validation
originalCriterion: Execute original Sentinel and converted Advanced Hunting queries with complete current-hash evidence on their respective surfaces.
applicability: Active migration in Qualification for every packaged pair; native/unpaired query tests remain QUAL-RUNTIME-01.
category: qualification
howPerformed: Execute exact persisted source KQL in the locked Log Analytics workspace and target KQL in the selected XDR Advanced Hunting tenant with approved bindings; reconcile complete paired query inventories.
expectedEvidence: [source/target query inventory and hashes, independent provider/target bindings, complete response files, schemas, errors and row counts]
passCriteria: Both exact query families execute successfully and completely with current real-provider evidence. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified, never a runtime-pass claim; safety gates remain non-waivable.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.runtime Sentinel SDK and Advanced Hunting execution/import routes
```

## TK-Q02 — Runtime output-schema binding

Zero rows can establish returned schema, but cannot satisfy positive-data or
alert-firing checks.

```yaml check-definition
id: TK-Q02
checklist: migration
contentType: all
title: Migrated Runtime Output-schema Binding
originalCriterion: Verify actual target query output schema for custom details and required migrated query/entity bindings.
applicability: Active migration Qualification with schema-bound detection/workbook outputs, especially custom details.
category: qualification
howPerformed: Compare actual returned provider schemas for exact current queries with required columns/types and reviewed bindings; retain absent or mismatched columns even when execution itself succeeds.
expectedEvidence: [query hashes, actual schema arrays, required binding/type inventory, expected versus observed columns, raw provider response refs]
passCriteria: Required runtime columns/types and bindings are proven by actual schemas; column counts or fabricated schemas are insufficient. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; E2E-G01 cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.runtime and migration.converter runtime custom-detail binding checks
```

## TK-Q03 — Complete provider families and honest failure classification

Retain raw failures and source-waived outcomes. Authoring exceptions are not
successful live Qualification.

```yaml check-definition
id: TK-Q03
checklist: migration
contentType: all
title: Provider-family Completeness and Failure Classification
originalCriterion: Do not mix providers within a query family or use fallback to hide genuine KQL errors; preserve narrow source-waived evidence.
applicability: Active migration runtime validation, fallback/import and reused authoring evidence.
category: qualification
howPerformed: Check complete-family provider/run/target/query bindings; permit documented complete-family reruns only for eligible provider failures; retain IdentityInfo source-waived raw errors and all unexecuted/failed outcomes.
expectedEvidence: [family inventory, provider and dispatch bindings, original and retry response refs, failure classifications, exact source-waiver reason if present, current query hashes]
passCriteria: Current paired families have genuine complete successful execution without disguised errors or unsupported fallback. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; raw source-waived status remains distinct and real-provider/target/authorization gates cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.runtime, reporting.runtime_report_references and migration.source_runtime_waiver
```

## TK-Q05 — Exact paired workbook fixture assertions

Non-ingestible fixture harnesses are supplementary; E2E-Q04 still requires
authored queries against injected live data.

```yaml check-definition
id: TK-Q05
checklist: migration
contentType: xdr-workbooks
title: Paired Workbook Exact-result Qualification
originalCriterion: Run reviewed workbook fixtures through independent Sentinel and Advanced Hunting providers and compare exact expected results.
applicability: Active workbook migration with a supported reviewed paired fixture family in Qualification.
category: qualification
howPerformed: Execute the hash-bound source/target harness family through independent providers and assert schema, cells, multiplicity and ordering against reviewed expected results.
expectedEvidence: [fixture config/provenance, source/target workbook hashes, exact harness query hashes, independent provider response refs, expected and observed result assertions]
passCriteria: Every applicable fixture case passes exact assertions with current real-provider evidence; no DCR injection claim follows. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; real-provider safety cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.workbook_qualification and migration._workbook_core.workbook_fixtures
```

## TK-Q09 — Shared-fixture marked query parity

Do not compare unrelated rows or pair files by their directory order.

```yaml check-definition
id: TK-Q09
checklist: migration
contentType: xdr-detections
title: Shared Scenario Source-row Query Parity
originalCriterion: Exact AR and CD queries observe the same unique scenario markers and identical expected matching source-row keys.
applicability: Every packaged Sentinel AR to XDR CD pair in active migration Qualification.
category: qualification
howPerformed: Bind each pair to one reviewed logical mock fixture and coordinated injection receipt; compare exact query outputs by defined stable keys and expected malicious/benign scenarios on both surfaces.
expectedEvidence: [provenance pair map, shared fixture hash, injection ledger ref, expected match keys, source/target exact query hashes and result refs, missing/extra keys]
passCriteria: Both queries observe the expected marked source records without missing or unexpected scenario matches. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; synthetic sample-row fallback cannot satisfy E2E-G01.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: Planned real marked-query parity adapter; generic qualification.parity fallback is not acceptable evidence
```

## TK-Q10 — Strict alert comparison dimensions

This comparison is shared with E2E-Q03; do not run a second injection or
activation merely to produce another check result.

```yaml check-definition
id: TK-Q10
checklist: migration
contentType: xdr-detections
title: Strict Sentinel and XDR Alert Comparison
originalCriterion: Compare alert counts, match keys, expected malicious matches, severity, tactics, entities and decisive evidence.
applicability: Each packaged migrated AR/CD pair with real captured alerts.
category: qualification
howPerformed: Normalize independently captured alerts, reject duplicate or missing detection/match keys, and compare all defined dimensions against nonempty reviewed expected key sets.
expectedEvidence: [raw source/target alert capture refs, alert IDs, normalized captures, expected keys, dimension-level comparisons, missing/extra/benign matches]
passCriteria: Every strict comparison dimension passes and expected positive alerts exist on both sides; empty-equals-empty is not success. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified; live capture provenance and safety cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.alert_parity.compare_alert_captures with real capture provenance checks
```

## E2E-Q03 — Complete migrated-pair alert parity

This is an overlay over individual firing, not a substitute for E2E-Q02.
Unpaired packaged detections still need their individual firing tests.

```yaml check-definition
id: E2E-Q03
checklist: migration
contentType: xdr-detections
title: Sentinel AR to XDR CD End-to-end Alert Parity
originalCriterion: Sentinel and XDR detection alerts actually fire for every migrated pair from shared mock injection and satisfy strict alert parity.
applicability: Every packaged source-provenance AR/CD pair in active migration Qualification.
category: qualification
howPerformed: Reconcile full packaged pair inventory with E2E-Q01 injection, E2E-Q02 firing, TK-Q09 row parity, TK-Q10 alert comparison and TK-Q11 controlled lifecycle/cleanup evidence; prohibit separate AR/CD payloads or accidental duplicate ingestion.
expectedEvidence: [packaged pair inventory, shared fixture/injection refs, source and target alert IDs, row and alert comparison refs, per-pair coverage results, final disabled-state receipts]
passCriteria: Every packaged migrated pair has positive scenario-correlated alerts, strict parity and safe cleanup from the same reviewed injection. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Conditionally Qualified with failed parity visible; authorization/privacy/target/real-provider and cleanup gates cannot be waived.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned pair-coverage rollup reusing qualification.alert_parity start/complete/abort and real query/alert collectors
```
