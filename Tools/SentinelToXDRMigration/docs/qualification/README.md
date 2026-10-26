# PR qualification checklists

Specification version: **1.0.0**. Source review date: **19 October 2026**.

These documents define Stream 1 of the PR Qualification Toolkit. They unify
the content review team's criteria with existing toolkit contracts and the
maintainer's end-to-end requirements. They are specifications, not execution
receipts, proof of implementation, or permission to access a tenant.

## Checklist architecture

| Checklist | Operator Flow Guide | Scope | Execution boundary |
|---|---|---|---|
| [Validation](validation-checks.md) | [Validation Flow Guide](../validation-flow-readme.md) | General Sentinel/XDR solution PRs; offline/CI checks, authoring, package inventory, mock existence/schema | No lab writes. Import current CI and approved external evidence rather than silently performing network operations. |
| [Qualification](qualification-checks.md) | [Qualification Flow Guide](../qualification-flow-readme.md) | General solution runtime, live fixtures, alerts, portal content and human review | Explicit Qualification selection and separate exact-scope approvals. First check is `QUAL-00`. |
| [Migration](migration-checks.md) | [Migration Flow Guide](../migration-flow-readme.md) | Additional source-to-target checks for Sentinel-to-Defender-XDR migrations | Overlay only; static checks augment Validation and live checks augment Qualification. |

> **No-Code / Chat-Based Execution:** The entire Validation, Qualification, and Migration experience can be completed conversationally with **no code** using LLM agents (`XDR Solution Manager` / `.github/agents/xdr-solution-manager.agent.md` and `sentinel-xdr-end-to-end-orchestrator`). See each Operator Flow Guide above for example chat prompts alongside the deterministic CLI commands.

Migration is active only when the PR introduces or changes a migration of
Sentinel content into `XDR Detections/` or `XDR Workbooks/`, with a defensible
source/target pairing. Folder presence or native XDR authoring alone is not
enough. Use provenance and PR change intent, including edits to a source of an
existing pair. Ambiguous pairing is unresolved, not silently non-applicable.
Never invent a Sentinel counterpart for a native XDR item.

The [canonical workflow](../../agent-workflows/end-to-end-migration.md) remains
the authority for existing tool operations, approvals and deployment gates.
This specification adds review outcomes; it does not bypass existing execution
gates, enable a blocked provider, or authorize runtime edits to tooling.
Implementing these definitions in an engine is a separate maintainer task.

## Machine-readable format

Each check has a readable Markdown section followed by exactly one fenced
block whose opening line is ` ```yaml check-definition ` (without the spaces).
The block contains a single YAML mapping. A runner must parse these mappings,
not interpret arbitrary prose or execute strings from definitions.

All blocks use exactly these keys:

| Key | Type / allowed values |
|---|---|
| `id` | Globally unique, stable string |
| `checklist` | `validation`, `qualification`, `migration` |
| `contentType` | Content scope string; mixed scopes use `all` and explain selection in `applicability` |
| `title` | Reviewer-facing title |
| `originalCriterion` | Exact or closely preserved source wording; toolkit-derived criteria are explicitly attributed |
| `applicability` | Declarative scope text, not executable code |
| `category` | `validation`, `qualification`, `human-review` |
| `howPerformed` | Procedure or adapter contract, not an executable shell command |
| `expectedEvidence` | Nonempty list of required observations and evidence references |
| `passCriteria` | Actual pass condition and explicit waiver treatment |
| `sourceChecklist` | `master-excel`, `pr-checklist-2-docx`, `toolkit-contract`, `user-e2e-requirement` |
| `automationStatus` | `automated`, `agent-qualified`, `human-review` |
| `responsible` | Existing implementation or explicitly marked planned adapter/agent |

`automationStatus` describes the intended execution mechanism, not a claim
that an adapter already exists. `responsible` explicitly marks planned work.
An unavailable implementation produces `SKIPPED` with a reason, never `PASS`;
unavailable safety checks remain blocking. Existing module names are relative
to `Tools/SentinelToXDRMigration` unless prefixed with `.script/`.

Category and mechanism are independent. A live deterministic comparison can
be `qualification`. A human accepting an exception does not turn its result
into a deterministic pass. Governance is a grouping, not a fourth category.

## Results, author evidence and rollups

Results belong in execution artifacts, not in these definitions. Bind each
check instance to the PR base/head SHA, solution/content identity, definition
version/hash, input hashes and evidence references. Preserve original results,
attempts, timestamps and actor decisions.

| Result | Meaning |
|---|---|
| `PASS` | Current evidence establishes the check's actual pass criteria |
| `FAIL` | Observed evidence contradicts the criteria |
| `SKIPPED` | Not executed; record why, including missing implementation or unavailable environment |
| `BLOCKED` | Missing prerequisite, authorization, trustworthy evidence or safety readiness |
| `NOT_APPLICABLE` | Proven outside scope; include applicability evidence, not merely an empty scan |
| `WAIVED_WITH_AUTHOR_EVIDENCE` | Prior `FAIL` or `SKIPPED` has an explicit, evidence-supported author exception; original outcome remains recorded |

An exception record in `decision-manifest.json` must identify the check
instance and affected items, previous outcome, author identity, justification,
evidence reference, input/head hashes, decision time and acknowledged scope.
The runner must verify that the evidence reference resolves and is current.
A bare comment, asserted approval, arbitrary status edit or stale evidence is
insufficient. Do not assume the existing `decision-manifest-v1` already accepts
these fields; the engine needs a compatible versioned extension or linked
exception projection that preserves existing decision records.

Only `FAIL` and `SKIPPED` are eligible for this transition. A `BLOCKED` safety
gate cannot be relabeled to make it waivable.

**Non-waivable safety gates:**

- `TK-G02`: target scope and identity.
- `TK-G03` and `TK-G04`: authorization and effective access.
- `TK-G07`: privacy and safe evidence export.
- `E2E-G01`: real-provider evidence; no simulated fallback.
- `TK-G06`: approved browser scope, including prohibited write actions.
- `TK-Q11`: controlled activation and return to disabled state.

This list does not permit waiving authorization, privacy or target checks
embedded in another check. Never dispatch an unsafe action to obtain evidence.
No waiver grants authentication, deployment, activation, ingestion, cleanup,
permission changes or publication rights.

| Rollup | Conditions |
|---|---|
| `Validated` | All applicable checks in validation-checks.md plus active migration validation checks pass; complete inventory with no author exclusions or waivers |
| `Partially Validated` | All required safety gates pass; no unresolved applicable failures/skips/blocks; at least one valid author exception or acknowledged inventory exclusion |
| `Qualified` | `QUAL-00` passes with `Validated`; all applicable checks in qualification-checks.md and active migration live/human checks pass; no exceptions or excluded inventory |
| `Conditionally Qualified` | `QUAL-00` and safety gates pass; all other applicable checks pass or have valid author exceptions, with no unresolved failures/skips/blocks; at least one exception exists or upstream Validation is `Partially Validated` |

Anything else is not a successful rollup. Report unresolved human decisions as
pending/blocked, not silently passed. `QUAL-00` itself is not waivable.
`NOT_APPLICABLE` instances do not count as executed passes. State a zero-content
denominator explicitly; never infer 100% coverage from it.

Checklist placement determines the execution phase. For example, `QUAL-00`
and the `category: validation` safety/evidence gates in qualification-checks.md
are deterministic Qualification prerequisites or finalizers; they are not
inputs to the upstream Validation rollup. This avoids a circular prerequisite.
The migration overlay uses category to choose its base rollup as described above.

`E2E-V01` can pass when every content item is packaged **or** all exclusions
are explicitly acknowledged by the author in `decision-manifest.json`.
The second case still forces `Partially Validated`, even though that particular
check passes. Subsequent live scope is every packaged item; report the full
source inventory and exclusions alongside it. Conditional outcomes never claim
that excluded items or waived behavior were tested.

## Inventory and evidence contract

- Inventory all solution content recursively, including renamed/deleted items,
  explicit package selections and referenced dependencies. Distinguish logical
  components from install/registration resources, supporting assets and docs.
- Expand impact through parser, connector, query and package dependencies.
  A changed source can activate checks for an unchanged dependent output.
- Detection and workbook mock validation checks existence and schema-valid
  JSON for **all packaged** items. It does not establish semantic adequacy.
  Map shared fixtures explicitly; do not require one physical file per item.
- Converted AR/CD pairs use the same reviewed logical scenario. Native and
  unpaired content receives individual tests, not invented parity partners.
- Qualification must associate query/alert/UI captures with current inputs,
  the selected target, a real provider, timestamps and raw evidence file
  references/hashes. Imported-live evidence needs verifiable collection
  provenance. Self-reported booleans and hashes alone do not prove execution.
- Record what was checked, expected versus observed values, source file and
  JSON pointer/query identity, PR file/line links where valid, and where each
  evidence artifact can be inspected. Pin links to the reviewed commit.
- Preserve reviewer terms such as **Basics**, **Manage**, **regular rules**,
  **XDR rules**, **Actual result**, **Pass/Fail**, and **Comments**.
- Keep private lab evidence in controlled local artifacts. Publish only
  sanitized references/projections; do not export browser sessions or tokens.

## Known implementation boundaries

The current generic `qualification/orchestrator.py`, `mock_data.py`,
`parity.py` and `workbook_playwright.py` have paths that can construct successful
results without real callbacks. Such results cannot satisfy `E2E-G01`.
The stricter `workbook_qualification.py`, `workbook_browser.py` and
`alert_parity.py` contracts are useful foundations, but do not establish
universal portal coverage by themselves.

Current workbook fixture harnesses can be non-ingestible and are separate from
`E2E-Q04` live injected-data proof. Current batch alert parity invokes ingestion;
coordinate exactly-once shared ingestion rather than ingesting both in a prior
stage and again during parity. Respect schedule/ingestion timing, especially
Continuous/NRT. Automatic solution-first DCR discovery and some workbook
provider acceptance remain limited; do not infer support or claim it passed.

Existing source-waived or environment-blocked authoring outcomes are not full
live qualification. Keep the original source error and evaluate any proposed
review exception under this document without weakening actual execution gates.

## Sources and reconciliation

| Source key | Source / locator |
|---|---|
| `master-excel` | `Microsoft Sentinel Content Review Checklist - Master.xlsx` (content review team checklist; normalized into [validation-checks.md](validation-checks.md) and [qualification-checks.md](qualification-checks.md)) |
| `pr-checklist-2-docx` | `Checklist 2.docx - Pull Request Validation Checklist` (PR validation checklist; normalized into [validation-checks.md](validation-checks.md) and [qualification-checks.md](qualification-checks.md)) |
| `toolkit-contract` | [Toolkit README](../../README.md), canonical workflow and referenced implementation |
| `user-e2e-requirement` | Maintainer requirements of 19 October 2026, including the packaged-inventory and non-waivable safety clarifications |

The external checklist sources were reviewed through WorkIQ extraction, not a
binary-certified workbook import. All 12 visible sheets were considered.
TI Matching has five criteria (rows 4-8); its repeated row-one headers are not
checks. Historical Pass/Fail and automation cell values are not current results.
Source references may require internal access. Do not redistribute the source
documents or private evidence as part of a public solution package.

| Source section | Definitions covering the section |
|---|---|
| GET-STARTED | Setup references only; current authorization and execution procedures take precedence |
| Data Connectors, rows 3-42 | `VAL-DC-01`, `VAL-DC-02`, `VAL-URL-01`, `QUAL-DC-01`, `QUAL-TEXT-01`, `QUAL-RELEASE-01` |
| Sample data, rows 3-7 | `VAL-SAMPLE-01`, `E2E-V02`, `E2E-V03`, `QUAL-MOCK-01`, `TK-G07` |
| Logo, rows 3-14 | `VAL-LOGO-01`, `E2E-Q06` |
| Parsers, rows 3-9 | `VAL-PARSER-01`, `QUAL-PARSER-01`, `QUAL-TI-01`, `VAL-URL-01` |
| Analytic Rule Templates, rows 3-38 | `VAL-RULE-01`, `QUAL-RULE-01`, `QUAL-TI-01`, `E2E-Q02` |
| TI Matching, rows 4-8 | `QUAL-TI-01`; cross-applies to rules, hunts, parsers, workbooks and playbooks |
| Hunting Queries, rows 3-38 | `VAL-RULE-01`, `QUAL-RULE-01`, `QUAL-TI-01`, `QUAL-RUNTIME-01` |
| Workbooks, rows 3-29 | `VAL-WB-01`, `VAL-LOGO-01`, `TK-V07`, `E2E-V03`, `E2E-Q04..Q06`, `TK-Q06`, `QUAL-TEXT-01`, `QUAL-RELEASE-01` |
| Solutions, rows 4-27 | `VAL-CI-01`, `VAL-PKG-01`, `TK-Q07`, `E2E-Q01..Q06`, `QUAL-DC-01`, `QUAL-PARSER-01`, `QUAL-PLAYBOOK-01` |
| Solutions, rows 39-72 | `VAL-PR-01`, `VAL-META-01`, `VAL-PKG-02`, `VAL-URL-01`, `VAL-RELEASE-01`, `TK-V10..V13`, `QUAL-URL-01`, `QUAL-RELEASE-01` |
| Playbooks, rows 3-16 | `VAL-PLAYBOOK-01`, `QUAL-PLAYBOOK-01`, `QUAL-TI-01`, `TK-G07` |
| Notebooks, rows 3-19 | `VAL-NOTEBOOK-01`, `QUAL-NOTEBOOK-01`, `QUAL-URL-01`, `TK-G07` |
| Checklist 2 - PR validations | `VAL-CI-01`, `QUAL-00` |
| Checklist 2 - Basics / Manage | `VAL-PKG-01`, `E2E-Q05` |
| Checklist 2 - XDR artifacts / regular rules | `VAL-ARTIFACT-01`, `QUAL-RUNTIME-01`, `E2E-Q02` |
| Checklist 2 - package version / mainTemplate properties | `VAL-PKG-02`, `TK-V11` |
| Checklist 2 - short URLs / createUiDefinition | `VAL-URL-01`, `QUAL-URL-01`, `VAL-PKG-01`, `E2E-Q05` |

Toolkit families retain their IDs where possible. Migration-only
`TK-V01..V05`, `TK-V08..V09`, `TK-Q01..Q03`, `TK-Q05`, `TK-Q09..Q10`,
`MIG-WB-01` and `E2E-Q03` live in the overlay. General runtime/dependency,
workbook interaction/readback, DCR and lifecycle checks include
`QUAL-RUNTIME-01`, `TK-Q04`, `TK-Q06..Q08` and `TK-Q11`.
General inventory uses `E2E-V01`, not the migrated-source denominator;
`E2E-V04` reconciles final live evidence and coverage.
`TK-G01` and `TK-G11` are enforced by the rollup/evidence rules;
`TK-G08` by `VAL-ARTIFACT-01` and `TK-Q07`; `TK-G09`, `TK-G10`, `TK-G13`,
and `TK-G14` by `VAL-OPS-01`; `TK-G12` by migration `TK-Q03`.

### Policy interpretation requiring review

- Historical 50-character name criteria differ from current instruction
  targets/hard limits. Use the current kind-specific contract and disclose
  differences; never fail a hunt for missing analytic scheduling fields.
- "Not in TCS scope" is an ownership marker, not a pass or universal exclusion.
- Legacy V2 locations, standalone-copy guidance and post-merge gallery checks
  retain their source meaning but need explicit applicability. V3.1 packaging
  remains the hybrid route; do not downgrade content to a historical layout.
- Distinguish package release version, content version, content schema version
  and ARM schema version. Record the exact field being compared.
- Visual quality, detection usefulness, owner permissions and MSTIC/Connector
  team sign-off remain human responsibilities where evidence is not sufficient.

## NPF operating principles

Start with a review-ready, trustworthy PR, not a target number of agents.
Reuse deterministic validators, use bounded agents for semantic/visual
assessment, retain named human accountability and stop when evidence is
missing. Measure review effort, rework, escaped defects and cost per successful
outcome. Promote repeated, adjudicated feedback into reviewed definitions and
regression tests; never let an agent automatically relax this standard.
