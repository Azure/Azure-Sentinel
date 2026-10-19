# Validation checklist

Offline/CI and authoring checks for general Sentinel/XDR solution PRs.
See the [result and exception contract](README.md#results-author-evidence-and-rollups).
Existing CI evidence and externally approved observations may be imported;
this checklist does not authorize cloud reads or writes. Active migration
validation checks are additional prerequisites, not replacements.

## VAL-CI-01 — Existing PR validations passed

Review the exact PR head and the complete applicable official check set.

```yaml check-definition
id: VAL-CI-01
checklist: validation
contentType: all
title: Existing PR Validations Passed
originalCriterion: Verify that all validations have passed for the given Pull Request.
applicability: Every solution PR, with or without migration.
category: validation
howPerformed: Consume head-SHA-bound required CI results and official build-and-validate receipts; retain individual failures and skips.
expectedEvidence: [PR head SHA, required check inventory, observed conclusions, CI run URLs, local receipt file references]
passCriteria: All applicable official checks completed successfully for current inputs. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and a current evidence ref, yielding Partially Validated, never PASS; safety gates cannot be waived.
sourceChecklist: pr-checklist-2-docx
automationStatus: automated
responsible: .script/local-validation/build-and-validate.ps1 and planned PR CI evidence adapter
```

## E2E-V01 — Content inventory and acknowledged exclusions

Count logical content, not duplicate install/registration resources. Acknowledged
exclusions permit this check to pass but force a Partially Validated rollup.

```yaml check-definition
id: E2E-V01
checklist: validation
contentType: all
title: Content Inventory and Package Coverage
originalCriterion: Package 100% of solution content items or explicitly acknowledge partial inventory exclusions in decision-manifest.json.
applicability: Every solution PR; inventory current content, removals, selections and dependencies regardless of migration.
category: validation
howPerformed: Reconcile recursive logical content inventory with source selections and packaged resources; verify each exclusion has a current explicit author acknowledgement in decision-manifest.json.
expectedEvidence: [complete inventory with hashes, packaged item identities, exclusion identities and reasons, author decision records, decision-manifest.json reference, expected and observed counts]
passCriteria: Every content item is packaged or explicitly excluded with current author acknowledgement and evidence ref. Acknowledged exclusions force Partially Validated even when this check is PASS. Other FAIL or SKIPPED results may become WAIVED_WITH_AUTHOR_EVIDENCE only with author justification and evidence ref; safety gates cannot be waived.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned PR inventory adapter reusing solution_manager.qualification.deployment_planning and solution_manager.reporting.decision_manifest
```

## E2E-V02 — Detection mock data existence and schema

Cover all packaged Sentinel ARs and XDR CDs. Semantics belong in Qualification.

```yaml check-definition
id: E2E-V02
checklist: validation
contentType: all
title: Detection Mock Data Existence and Schema
originalCriterion: Mock data files exist and are schema-valid JSON for all packaged Sentinel Analytic Rules and Defender XDR Custom Detections.
applicability: Every packaged detection, including source-only ARs and native XDR CDs; migration is not required.
category: validation
howPerformed: Map each detection identity to existing nonempty JSON fixtures and an identified schema; parse JSON and validate record shapes and types without inferring scenario semantics.
expectedEvidence: [packaged detection inventory, detection-to-fixture mappings, fixture file paths and hashes, schema identity and version, per-file parse and schema results]
passCriteria: Every packaged AR and CD maps to existing schema-valid JSON mock data; shared files are allowed with explicit mappings. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; no semantic correctness claim follows.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned fixture inventory/schema adapter; reuse reviewed mock artifacts and ingestion contract schemas
```

## E2E-V03 — Workbook mock data existence and schema

Cover packaged Sentinel and Defender workbooks, including their query data needs.

```yaml check-definition
id: E2E-V03
checklist: validation
contentType: workbooks
title: Workbook Mock Data Existence and Schema
originalCriterion: Mock data files exist and are schema-valid JSON for all packaged Workbooks.
applicability: Every packaged Sentinel or XDR workbook, regardless of migration.
category: validation
howPerformed: Map workbook and nested query identities to existing JSON fixtures and declared schemas; validate file existence, JSON shape and types, not expected query behavior.
expectedEvidence: [packaged workbook inventory, query-to-fixture mappings, fixture paths and hashes, schema references, observed JSON/schema results]
passCriteria: All packaged workbooks have mapped schema-valid JSON mock files with no unaccounted query data dependency. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; live data and semantics remain unverified.
sourceChecklist: user-e2e-requirement
automationStatus: automated
responsible: Planned workbook fixture coverage adapter reusing workbook inventory and fixture metadata
```

## VAL-PKG-01 — Basics and createUiDefinition component counts

Static counts must agree across selection, package and UI declarations.

```yaml check-definition
id: VAL-PKG-01
checklist: validation
contentType: solution-package
title: Package Component Count Validation
originalCriterion: Verify that the component counts are present and correct in createUiDefinition.json and Basics.
applicability: Solution selection, package or UI definition changes, including dependent component changes.
category: validation
howPerformed: Count unique logical selected components by type and compare with package resources and createUiDefinition count declarations; keep rendered UI proof separate.
expectedEvidence: [source selection reference, logical component inventory, package JSON pointers, UI count locations, expected and actual counts]
passCriteria: All required component counts are present and equal, without double-counting registration resources. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: pr-checklist-2-docx
automationStatus: automated
responsible: Planned count reconciliation adapter reusing solution_manager.packaging.packaging and deployment_planning
```

## VAL-PKG-02 — Package version increment and consistency

The live baseline is evidence, not an assumed local version. Also covers Master
Solutions rows 44, 46 and 52; schema versions are separate fields.

```yaml check-definition
id: VAL-PKG-02
checklist: validation
contentType: solution-package
title: Package Version Increment Validation
originalCriterion: Ensure that the package version has been incremented from the latest version currently live.
applicability: New or updated solution packages; new offers require evidence that no live baseline exists.
category: validation
howPerformed: Compare canonical release versions against a current imported live-offer snapshot bound to publisher and offer; check ZIP name, package metadata and solution version consistency.
expectedEvidence: [publisher and offer identity, live baseline value and observation time, baseline evidence ref, proposed version values and JSON pointers, ZIP filename]
passCriteria: Updated release exceeds the proven live baseline and all package version fields agree; new-offer absence is evidenced. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; unavailable baseline is not an inferred pass.
sourceChecklist: pr-checklist-2-docx
automationStatus: automated
responsible: Planned live-baseline comparison adapter; reuse packaging version checks and .script/package-automation/catalogAPI.ps1 evidence
```

## VAL-META-01 — Solution metadata and branding

Review support, author, offer, domain and component references.

```yaml check-definition
id: VAL-META-01
checklist: validation
contentType: solution-package
title: Solution Metadata and Branding Validation
originalCriterion: Verify metadata, support information, author/provider details, domains, and Microsoft Sentinel branding.
applicability: Solution metadata, solution data or package metadata changes and new solutions.
category: validation
howPerformed: Apply current metadata/data contracts, identifier casing, support fields, path existence and branding checks; compare imported Content Hub identity evidence for updates.
expectedEvidence: [metadata file references, expected contract version, observed field values, field-level findings, Content Hub identity evidence ref when applicable]
passCriteria: Required fields and references conform to the applicable contract and supported offers do not use inappropriate personal author/support identities. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script/SolutionValidations, solution-data and solution-metadata instructions, planned contract-gap adapter
```

## VAL-RULE-01 — Detection and hunting query contracts

Apply kind-specific requirements; do not apply Scheduled-rule fields to hunts.
Native XDR detection structure is checked here; source-derived identity and
transformation contracts remain in the migration overlay.

```yaml check-definition
id: VAL-RULE-01
checklist: validation
contentType: all
title: Detection and Hunting Query Contract Validation
originalCriterion: Id is GUID and not duplicated; YAML structure is correct; review names, descriptions, dependencies, tactics, techniques and query fields.
applicability: Packaged or changed Analytic Rules, native or migrated XDR detections and Hunting Queries, including dependencies affected by the PR.
category: validation
howPerformed: Run YAML, identity, detection-schema and KQL checks; apply current kind-specific naming, field, MITRE, entity/custom-detail binding and query contracts; use the appropriate native or source-derived identity contract and record legacy checklist conflicts explicitly.
expectedEvidence: [rule or hunt paths and IDs, contract version, schema and KQL results, duplicate-ID search scope, field findings and source locations]
passCriteria: Applicable syntax and structural requirements pass with correct kind-specific fields and references. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; semantic intent is assessed separately.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script/local-validation/build-and-validate.ps1, validate-xdr-content.py, detection-schema and KQL tests, planned instruction-to-check mappings
```

## VAL-DC-01 — Data connector structure and dependencies

Covers Master Data Connectors template, naming, permissions, metadata and parser
banner checks; provider identity and instruction quality also need human review.

```yaml check-definition
id: VAL-DC-01
checklist: validation
contentType: data-connectors
title: Data Connector Contract Validation
originalCriterion: Compare the JSON with the relevant template and ensure properties, data types, permissions and parser dependencies are captured.
applicability: Packaged or changed connectors and their affected parser dependencies, regardless of migration.
category: validation
howPerformed: Validate applicable connector template/schema, IDs, names, datatype formats, permissions, query syntax, metadata and required parser references/banners.
expectedEvidence: [connector type and template version, file references, observed fields, query syntax results, parser dependency references, field-level differences]
passCriteria: All applicable structural/template checks pass and required dependencies are declared. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; declared permissions do not establish effective access.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script/dataConnectorValidator.ts and checker utilities; planned full template/banner adapter
```

## VAL-DC-02 — Function App connector artifacts

Inspect archives without executing submitted code.

```yaml check-definition
id: VAL-DC-02
checklist: validation
contentType: data-connectors
title: Function App Connector Artifact Validation
originalCriterion: Validate deployment and execution files, Function App ZIP contents, function-name bounds and template variables.
applicability: Function App connector additions or changes, including changes to Azure deploy files.
category: validation
howPerformed: Inspect referenced ARM/code/ZIP artifacts, required runtime dependencies such as .python_packages where applicable, name bounds and prohibited hostNameBindings; perform syntax checks without running connector ingestion.
expectedEvidence: [deployment and execution file references, ZIP entry inventory, runtime contract, syntax findings, expected and observed template fields]
passCriteria: All required artifacts and applicable runtime/template constraints are satisfied without unsafe archive entries. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; unsafe execution or privacy gates cannot be waived.
sourceChecklist: master-excel
automationStatus: automated
responsible: Planned Function App artifact adapter reusing repository JSON/ARM checks
```

## VAL-SAMPLE-01 — Sample data structure and sanitation

Representative scenario behavior is a Qualification responsibility.

```yaml check-definition
id: VAL-SAMPLE-01
checklist: validation
contentType: all
title: Sample Data Structure and Sanitization
originalCriterion: Sample values are populated and sanitized for customer or PII information.
applicability: Sample Data and packaged mock fixtures, including table catalog metadata.
category: validation
howPerformed: Apply array/catalog-specific JSON and email sanitation contracts, required field/type checks and the non-waivable TK-G07 privacy check.
expectedEvidence: [sample file paths and hashes, applicable schema, record and field counts, sanitized scan findings, privacy check reference]
passCriteria: Applicable sample contracts pass and TK-G07 passes. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; PII/privacy failures cannot be waived.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script/utils/sampleDataCheckers/sampleDataCheckers.ts and planned sample-schema adapter
```

## VAL-LOGO-01 — SVG logo contract

Technical validity does not replace the portal rendering check.

```yaml check-definition
id: VAL-LOGO-01
checklist: validation
contentType: logos
title: SVG Logo Technical Validation
originalCriterion: Logo needs to be in SVG format and under 5 Kb; prohibited constructs are absent and IDs are uniquely identifiable.
applicability: New or changed content logos, including workbook images and referenced package logos.
category: validation
howPerformed: Inspect SVG format/size, style and cls constructs, embedded PNG, xlink, data-name, title and ID constraints with existing logo checkers; record exact size policy.
expectedEvidence: [logo file reference, byte size, format, prohibited-construct findings, ID uniqueness results]
passCriteria: Applicable SVG contract checks pass; appearance at 75 pixels remains E2E-Q06. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script/utils/LogoChecker and planned precise source-contract reconciliation
```

## VAL-PARSER-01 — Parser structure and samples

Select generic or ASIM-specific instructions as applicable.

```yaml check-definition
id: VAL-PARSER-01
checklist: validation
contentType: parsers
title: Parser Structure and Test Input Validation
originalCriterion: Sample data is available for testing; parser definitions and relevant ASIM schema are identified.
applicability: Changed parsers and packaged parser dependencies.
category: validation
howPerformed: Validate YAML metadata, function names/aliases, versions, query syntax, sample references and applicable ASIM schema/filter contracts without deployment.
expectedEvidence: [parser and sample references, generic or ASIM contract identity, metadata findings, KQL syntax results, declared output schema]
passCriteria: Applicable structure/query contracts and test-input references are valid. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; returned-field semantics require QUAL-PARSER-01.
sourceChecklist: master-excel
automationStatus: automated
responsible: Repository parser/KQL and ASIM validators; planned parser checklist adapter
```

## VAL-WB-01 — Workbook structure and metadata

Apply Sentinel or XDR workbook schemas, not one schema to both formats.

```yaml check-definition
id: VAL-WB-01
checklist: validation
contentType: workbooks
title: Workbook Structure and Metadata Validation
originalCriterion: Workbook metadata, unique workbookKey, dependencies, preview images, version and templateRelativePath are correct.
applicability: Packaged or changed Sentinel and XDR workbooks and their metadata/assets.
category: validation
howPerformed: Validate applicable workbook schema, query syntax, identity and dependency fields, metadata version increment, referenced logos and PNG previews including black/white naming where required.
expectedEvidence: [workbook and metadata references, schema identity, nested query inventory, unique IDs, image file references, old and new metadata versions]
passCriteria: Applicable workbook contract and references pass; legacy chart-count/layout criteria remain visible for qualification review. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script workbook validators and validate-xdr-content.py; solution_manager workbook validation modules
```

## VAL-PLAYBOOK-01 — Playbook template and documentation

Do not deploy or authorize connections during static review.

```yaml check-definition
id: VAL-PLAYBOOK-01
checklist: validation
contentType: playbooks
title: Playbook Template and Documentation Validation
originalCriterion: Validate the Playbooks folder and Readme, templatization, connection variables and Deploy to Azure/Gov buttons.
applicability: Packaged or changed playbooks, custom connectors and referenced deployment templates.
category: validation
howPerformed: Apply ARM/resource/parameter/metadata checks, naming and length rules, connection references, required README sections and deployment-link structure; run TK-G07 for sensitive data.
expectedEvidence: [template and README paths, naming findings, ARM/resource results, connection variables, button target references, privacy evidence ref]
passCriteria: Applicable template, naming and documentation contracts pass and TK-G07 passes. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: master-excel
automationStatus: automated
responsible: .script/playbooksValidator.ts and utilities; planned documentation completeness adapter
```

## VAL-NOTEBOOK-01 — Notebook structure and dependencies

Do not execute arbitrary notebook cells during offline validation.

```yaml check-definition
id: VAL-NOTEBOOK-01
checklist: validation
contentType: notebooks
title: Notebook Structure and Dependency Validation
originalCriterion: Notebook uses standard header information, documented dependencies and configuration; sample data is provided when possible.
applicability: Packaged or changed notebooks and referenced code/data.
category: validation
howPerformed: Parse notebook JSON, inventory code/data/API dependencies, check required explanatory sections and config.json or msticpyconfig.yaml references, and scan stored outputs through TK-G07.
expectedEvidence: [notebook file reference, cell/dependency inventory, configuration and sample refs, missing-section findings, privacy evidence ref]
passCriteria: Applicable structural and dependency requirements pass with no privacy failure. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; external-file exceptions require QUAL-NOTEBOOK-01.
sourceChecklist: master-excel
automationStatus: automated
responsible: Planned notebook static adapter
```

## VAL-URL-01 — Link inventory and static references

Actual short-link opening and expected destinations are checked in Qualification.

```yaml check-definition
id: VAL-URL-01
checklist: validation
contentType: all
title: URL and Changed-Reference Inventory
originalCriterion: Verify short URLs in mainTemplate.json and createUiDefinition.json and check links when files move or change.
applicability: All changed content and package URLs, plus incoming references to moved or deleted files.
category: validation
howPerformed: Extract URLs including Package files, identify additions/changes and target moves, check syntax/local references and applicable locale/easy-access naming rules; prepare live resolution scope.
expectedEvidence: [old and new URLs, source file/line or JSON pointer, incoming reference list, local target existence, static checker results]
passCriteria: URL inventory is complete and applicable static rules pass; no reachability claim is made. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: pr-checklist-2-docx
automationStatus: automated
responsible: .script/documentsLinkValidator.ts plus planned package-inclusive URL inventory adapter
```

## VAL-RELEASE-01 — Release notes

Keep reviewer terminology and exact version/date evidence.

```yaml check-definition
id: VAL-RELEASE-01
checklist: validation
contentType: solution-package
title: Release Notes Format and Coverage
originalCriterion: Check release note text and format.
applicability: Solution changes requiring release notes under the current release-notes instructions.
category: validation
howPerformed: Check path, three-column table, canonical versions, descending order, DD-MM-YYYY dates, nonempty history and correspondence to current release.
expectedEvidence: [ReleaseNotes.md reference, parsed rows, expected release version, date/ordering findings, changed component inventory]
passCriteria: Required release notes are present and structurally valid with current release coverage. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated.
sourceChecklist: master-excel
automationStatus: automated
responsible: solution_manager.packaging.release_notes and planned read-only release-note validation adapter
```

## VAL-PR-01 — PR review information and deletion accounting

A filled template is not proof that a risky removal is approved.

```yaml check-definition
id: VAL-PR-01
checklist: validation
contentType: all
title: PR Review Information and Change Accounting
originalCriterion: Ensure the PR review template is filled out; double-check deletions and merge-conflict resolutions.
applicability: Every solution PR, especially deletions, renames and conflict resolutions.
category: validation
howPerformed: Compare PR description with repository template; inventory deletions/renames and expected dependent changes; require explicit unresolved-impact records for human review.
expectedEvidence: [PR body and template refs, base/head SHA, deleted/renamed items, dependency impact list, author explanations and evidence refs]
passCriteria: Required review information and complete change accounting are present without unrecorded removals. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; required safety authorizations remain separate.
sourceChecklist: master-excel
automationStatus: automated
responsible: Planned PR metadata/diff adapter and content review owner
```

## VAL-ARTIFACT-01 — XDR artifacts and source protection

Missing artifacts must be requested from the author, not silently reconstructed.

```yaml check-definition
id: VAL-ARTIFACT-01
checklist: validation
contentType: all
title: XDR Artifact Completeness and Source Protection
originalCriterion: Verify XDR artifacts shared in the PR; if absent, ask the author to provide them.
applicability: PRs containing or changing packaged XDR content, including native content.
category: validation
howPerformed: Verify required content, package and evidence references exist and match current hashes; account for source edits and edited generated files without overwriting them.
expectedEvidence: [expected and observed artifact inventory, file/hash references, missing artifact requests, source/generated-file change inventory]
passCriteria: Required artifacts are present/current and source changes are explicit. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; unsafe overwrites or privacy failures are not authorized.
sourceChecklist: pr-checklist-2-docx
automationStatus: automated
responsible: Planned PR artifact adapter reusing solution_manager.reporting.evidence and migration conflict checks
```

## TK-V06 — Workload and connector provenance

These general XDR dependencies apply to native as well as migrated content.

```yaml check-definition
id: TK-V06
checklist: validation
contentType: all
title: Workload and Connector Dependency Provenance
originalCriterion: Validate workload vocabulary and dependency records; unresolved dependency review blocks readiness.
applicability: Packaged XDR detections/workbooks or changed dependency declarations.
category: validation
howPerformed: Validate record shapes, workload vocabulary, connector/data-type references and review disposition; exclude platform-reference inputs such as Watchlist from telemetry dependency requirements.
expectedEvidence: [dependency record locations, declared workloads/connectors, resolved table references, review decision refs, validation findings]
passCriteria: Applicable dependency records conform and no required review is unresolved. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated without changing existing deployment gates.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.dependencies and workbook_dependencies
```

## TK-V07 — Workbook function dependencies

Registration and deployment ordering do not prove runtime function availability.

```yaml check-definition
id: TK-V07
checklist: validation
contentType: workbooks
title: Workbook Function Dependency Integrity
originalCriterion: Bind required workspace functions to packaged definitions, aliases and current hashes; resolve actual parser installation dependencies.
applicability: Packaged Sentinel/XDR workbooks invoking parser or workspace functions.
category: validation
howPerformed: Check definition paths, aliases, hashes and underlying tables; distinguish built-in ASIM and Watchlist functions; verify unconditional required parser installation and actual saved-search dependsOn references.
expectedEvidence: [query/function references, definition hashes, builtin classification, package resource pointers, expected and observed dependency edges]
passCriteria: Function provenance and installation dependencies match the applicable workbook contract. FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; runtime availability remains separate.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.workbook_functions and solution_manager.packaging.packaging
```

## TK-V10 — Package candidate and archive integrity

Candidate creation is not package acceptance.

```yaml check-definition
id: TK-V10
checklist: validation
contentType: solution-package
title: Package Candidate and Archive Integrity
originalCriterion: Bind candidate inputs and artifacts and verify exact ZIP contents without stale, duplicate or operational entries.
applicability: Generated or changed solution packages, including V3.1 hybrid candidates.
category: validation
howPerformed: Validate selected input hashes, candidate/run identity, exact mainTemplate/createUiDefinition ZIP bytes and safe archive entries; prevent older package nesting.
expectedEvidence: [candidate identity, input manifest, artifact hashes, ZIP entry inventory, byte comparison results, package receipt ref]
passCriteria: Package artifacts and archive match current selected inputs and the applicable package contract. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; privacy and unsafe execution remain blocking.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.workbook_validation and solution_manager.packaging.packaging
```

## TK-V11 — XDR package properties and resource identities

Also covers Checklist 2's required XDR properties in mainTemplate.json.

```yaml check-definition
id: TK-V11
checklist: validation
contentType: solution-package
title: XDR Package Properties and Registration Integrity
originalCriterion: Verify required XDR content properties and exact installation/registration identity, version and dependency contracts.
applicability: Packages containing XDR detections or workbooks, whether native or migrated.
category: validation
howPerformed: Validate required properties, disabled defaults, deployment flags, matching install/registration resources, dependency references and packageId/packageVersion/contentId/contentVersion values.
expectedEvidence: [mainTemplate JSON pointers, selected content IDs, deployment flag values, expected and actual identity quartets, resource and dependsOn findings]
passCriteria: All applicable XDR package properties and resource contracts pass. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; activation/target authorization is never waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: .script/local-validation/validate-xdr-content.py and solution_manager.packaging.packaging
```

## TK-V12 — Official receipt and evidence freshness

A copied receipt or a skipped validator cannot establish current execution.

```yaml check-definition
id: TK-V12
checklist: validation
contentType: all
title: Official Validation Receipt Integrity
originalCriterion: Require complete producer-bound validation receipts for the current candidate and preserve individual statuses.
applicability: Any check consuming CI, local validation or package-acceptance evidence.
category: validation
howPerformed: Verify producer identity, toolkit/content root, run/head/input bindings, artifact hashes and complete validator inventory; reject malformed, conflicting or stale evidence.
expectedEvidence: [receipt file refs, producer binding artifact, toolkit and input hashes, complete validator statuses, freshness comparison]
passCriteria: Evidence is complete and current for each claimed execution; skips remain skips. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; no waiver upgrades untrusted live evidence under E2E-G01.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.qualification.arm_acceptance and planned generic evidence binding adapter
```

## TK-V13 — ARM static scope and official template checks

Static approval is not live deployment authorization.

```yaml check-definition
id: TK-V13
checklist: validation
contentType: solution-package
title: ARM Template and Bounded Scope Validation
originalCriterion: Resolve resource types, parameters, conditions and nested scopes and retain applicable official ARM validation checks.
applicability: Package ARM changes or candidate acceptance; selected ARM method determines applicable evidence.
category: validation
howPerformed: Inspect exact resources, booleans and nested scopes; run/import official ARM-TTK when selected and all remaining applicable official checks; route lab-method execution to Qualification.
expectedEvidence: [ARM resource/scope inventory, parameter bindings, official check receipts, selected ARM validation method, unresolved expression findings]
passCriteria: Applicable static checks pass with no ambiguous or unauthorized resource scope. Only non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; target scope and permission grants cannot be waived.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.authoring.workbook_validation and .script/local-validation/build-and-validate.ps1
```

## TK-G07 — Privacy and safe evidence publication

Non-waivable safety gate. Email-only sample scans are not a complete PII review.

```yaml check-definition
id: TK-G07
checklist: validation
contentType: all
title: Privacy and Safe Evidence Export
originalCriterion: Keep secrets, private target identifiers, personal data, local paths and operational receipts out of published content and evidence.
applicability: All source/sample/package artifacts, decision manifests, screenshots and evidence exports; recheck newly captured Qualification evidence.
category: validation
howPerformed: Scan and review public projections, samples and captures; separate private receipts, browser sessions and credentials; verify sanitization before release.
expectedEvidence: [artifact inventory, sanitized scan findings, redaction review, public/private disposition, sanitized manifest and evidence file refs]
passCriteria: All exported artifacts satisfy privacy requirements and private material remains protected. FAIL, SKIPPED or BLOCKED cannot transition to WAIVED_WITH_AUTHOR_EVIDENCE; author justification cannot waive TK-G07 or permit a successful rollup.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.reporting.decision_manifest, reporting.evidence, qualification.readiness_support and privacy reviewer
```

## VAL-OPS-01 — Durable workflow and accountable decisions

Covers toolkit retry, budget, immutable-tooling and reviewer-delivery controls.

```yaml check-definition
id: VAL-OPS-01
checklist: validation
contentType: all
title: Durable Workflow and Decision Integrity
originalCriterion: Preserve attempts and failures, use bounded execution, prevent duplicate owners and version consumption, and retain accountable review decisions.
applicability: Toolkit-managed authoring or qualification runs and imported workflow evidence.
category: validation
howPerformed: Inspect run ownership, durable state, budget receipts, retry/reconciliation records and delivered review packets; confirm protected tooling was not modified as a runtime workaround.
expectedEvidence: [run/state refs, owner lease, attempt history, budget receipts, review acknowledgement refs, toolkit version/hash, package version action history]
passCriteria: Applicable operational controls are satisfied without hidden failures or unapproved execution. Non-safety FAIL or SKIPPED may become WAIVED_WITH_AUTHOR_EVIDENCE with author justification and evidence ref, yielding Partially Validated; authorization/privacy/target/provider safeguards remain non-waivable.
sourceChecklist: toolkit-contract
automationStatus: automated
responsible: solution_manager.core.workflow, coordinator, budget, review_notifications and planned operational receipt adapter
```
