# Sentinel to Defender XDR migration workflow

This is the canonical, agent-neutral workflow for authoring and migrating
Microsoft Sentinel solution content to Defender XDR Custom Detections and
Defender Workbooks. Agent
adapters must reference this document rather than redefine the process.

Deterministic behavior belongs to:

- `Tools\SentinelToXDRMigration`;
- `Tools\Create-Azure-Sentinel-Solution`; and
- the repository validation tools.

Agents coordinate these tools but must not reproduce conversion, validation,
packaging, deployment, or comparison logic in prompts.

## Immutable toolkit boundary

Migration execution must never modify the agent, its skills, backend tools,
schemas, tests, dependency metadata, workflow definitions, safety gates, or
capabilities. Treat these paths as read-only throughout Authoring,
Qualification, retries, and failure recovery:

```text
.github/agents/**
.github/skills/**
Tools/SentinelToXDRMigration/**
Tools/SolutionMigration/**
Tools/Create-Azure-Sentinel-Solution/**
```

If a protected component fails, record the failure and stop the affected
stage. Do not patch, replace, bypass, or reconfigure implementation code as a
runtime workaround. This agent can never perform such changes, regardless of
the requesting user's identity, repository role, ownership, or approval.
Implementation work must be performed manually or by a different development
agent outside the XDR Solution Manager.

## Runtime prerequisite

Run the toolkit only with Python 3.11 or 3.12. If the active interpreter is
outside that range, switch or install the interpreter before continuing.
Environment incompatibility is not permission to edit toolkit source during a
migration workflow.

## Profiles

### Authoring goal and capability boundary

The product goal is to migrate Microsoft Sentinel solutions to Defender XDR
and enable authors to publish validated content without waiting for unrelated
source-rule failures to be fixed. Autonomous best-effort candidate generation
and a human-reviewable batch in which reviewers can accept, change, or exclude
proposed mappings remain roadmap goals, not claims that the current CLI
provides autonomous research or batch review orchestration.

Today, the deterministic converter emits only mappings supported by its
existing rules and records uncertain mapping assumptions as `reviewRequired`.
That uncertainty must not hide query parse/runtime failures or other technical
errors. A rule that cannot be represented as a deployable Custom Detection
must remain visible in diagnostics outside deployable YAML; it must not be
silently dropped or emitted as an invalid placeholder. Future accept/change/
exclude decisions may resolve mapping ambiguity, but acceptance is not proof
of alert parity, does not erase technical failures, and does not approve
packaging, deployment, or any cloud write. Existing review, validation,
disabled-by-default, and exact-scope authorization gates remain in force.

### Authoring

`Discovery -> Conversion -> Validation -> Packaging -> Report`

Legacy offline Authoring does not require a tenant, workspace, deployment, mock
ingestion, or alert-parity test. New capability-version-1 CLI runs use the
candidate ARM lifecycle below; their default lab route requires an approved
target and independently verified deployment evidence before package acceptance.

### Versioned workbook and candidate ARM lifecycle

Published authored workbook JSON must use the clean `public-workbook-v1`
dependency contract described in the toolkit README. Keep reviewer accounts,
acceptance decisions, references, session context, source/conversion proofs
and query/reverse-delta histories only in gitignored local `Logs` receipts.
Use `workbook-publication-plan/clean` to import legacy proof without deleting it.
Cleaning preserves the actual Notebook, managed IDs and authored content version.
Incomplete historical connector coverage must be explicitly reviewed and completed,
not carried forward as a public exception.

Portable structural validation of public content does not establish authoring
acceptance. Authoring/apply/package operations require current hash-bound local
review evidence. Explicit standalone reproduction against a selected published
Git commit can use public dependencies without private receipts; it is not a
workflow approval and does not relax any candidate, official-check, environment
authorization or qualification gate.

New CLI runs persist `workbookCapabilityVersion=1` and default to
`armValidationMethod=lab-deployment`, in either explicitly selected profile.
Authoring may explicitly choose `--arm-validation-method arm-ttk`. Existing
runs never silently acquire workbook scope or change their validation method;
direct library initialization retains legacy defaults unless capability 1 is
explicitly requested.

The order is:

`Discovery -> Conversion -> content/static Validation -> V3.1 candidate ->
remaining official checks -> selected ARM validation -> accepted Packaging`

Keep frozen recursive workbook inventory and explicit selections separate from
detection coverage. Workbook-only solutions need no invented Analytic Rules,
rule IDs, runtime manifests, ingestion or alert parity. Exclusions remain
visible, and explicit empty `XDR Workbooks` selections stay empty.

A candidate is not accepted packaging or a successful release. Preserve its
artifacts and consumed version action for same-version retries. Use the official
`build-and-validate.ps1` receipt bound to the current candidate. Lab validation
replaces only ARM-TTK; remaining applicable official checks are mandatory.
For selected Defender Workbooks, both methods additionally require independent
installation, registration/provenance readback and repeat-install/update
contract evidence. ARM-TTK alone cannot establish that contract.

Versioned lab consent binds the selected run/lab, deployment operation and
allowed content/resource types. Hash/count changes within that scope require
fresh evidence, not automatically broader approval. Changed labs, operations
or type sets require renewed approval. Revocation blocks dispatch. The executor
also requires explicit immediate confirmation and verified access, disabled
content and ownership; consent never grants permissions or authorizes ingestion,
activation or cleanup. This is not a reinterpretation of legacy consent.

**Defender workbook dispatch remains blocked:** the evidence-based preflight
adapter checks target, authenticated ARM principal, effective control-plane
access, applicable role/deny assignments, disabled content and exact identities,
but the MicrosoftSecurity extension authentication/write contract is unverified.
Unknown evidence blocks dispatch. Do not replace this blocker with asserted
readiness flags, infer support from a mock, reuse an unrelated Graph/AH token
as the extension identity, or treat local tests as provider acceptance.

#### Candidate ARM metadata preflight

After the current candidate deployment plan exists, display the exact read plan
with `workflow-arm-preflight-plan`. Obtain separate affirmative metadata-read
approval through `workflow-arm-preflight-review`, bound to the displayed
`--preflight-plan-sha256` and recorded actor/reference. Execute the current plan
through `workflow-arm-preflight-execute`; withdraw approval through
`workflow-arm-preflight-revoke`. All commands require the explicit run ID.

Read consent binds the run, target and exact operation scope independently of
candidate/template hashes. Managed same-ID body/version changes require a fresh
plan and evidence, not automatically renewed approval of unchanged reads.
Changed IDs, URLs, operations or targets require renewed read approval.
Deployment consent and immediate write confirmation remain separate gates.

The production reader uses existing cached authentication in the pinned Azure
CLI profile, makes only planned metadata GETs, and correlates successful ARM
observations with that same authenticated bearer. Token claims or a local
account alone do not prove effective access. It never signs in, grants
permissions or attempts Graph extension reads with unverified credentials.
Read consent explicitly permits scoped ARM token acquisition/refresh through
the existing cached identity, not new credentials or Graph/AH token access.
Receipts preserve blocked/unknown findings and prior attempts; execution
rechecks current consent and candidate freshness. No preflight operation
authorizes installation, activation, ingestion, cleanup or browser execution.

New workbook-only Qualification runs record `validationMode=workbook-content`
before packaging, with query/UI checks not run. They require current independent
query and UI evidence before final Report. Mixed solutions retain all detection
runtime prerequisites before candidate generation; workbook UI proof remains
post-installation. A passed ARM candidate contract can supply workbook-only
Deployment evidence; do not run a detection-only deployer or invent detections.

### Toolkit-owner policy: managed same-ID updates

Toolkit-managed Defender Workbooks and XDR Custom Detections use stable-ID
upserts. Deploying approved content to the same ID intentionally replaces the
existing managed content; this is expected update behavior, including in labs.
Do not block an intended same-ID update merely because the remote content,
version or hash differs from the candidate or a previous deployment.

The intended workbook consumption model is read-only managed content.
Personalization uses a separate copy with its own identity; toolkit updates
must not discover or overwrite those copies. This policy defines the product
contract, not proof that the preview provider or portal currently enforces
read-only behavior.

Preflight must bind the selected target and intended resource identities,
verify effective access, and reject wrong returned IDs, ambiguous identity
mappings or operations outside the approved scope. A managed same-ID update
does not itself require an additional overwrite decision or previous-content
hash match. It still requires current candidate/review evidence, applicable
deployment consent and immediate write confirmation. Lab overwrite approval
does not authorize production, other identities, activation, deletion or
permission grants; XDR detections remain deployed disabled.

Keep exact post-write provenance/readback and package acceptance checks.
This managed cloud-update policy does not relax local source-file protection,
edited generated-file overwrite safeguards, or the QA prohibition on Save/Edit.

### Workbook Qualification and browser QA

`workbook-query-plan/review/execute` bind the exact reviewed fixture harness
family to the locked Qualification target. Linux Machines has 202 queries
across independent Sentinel and Advanced Hunting providers. Exact result
assertions, including schema, cells, multiplicity and ordering, are mandatory.
This fixture route does not authorize ingestion or prove live-panel telemetry.

`workbook-ui-plan/review/execute` use a reviewed, hash-bound browser configuration,
an existing private session and independently observed tenant, canonical content
and installed instance IDs. Require all seven check kinds: pickers, dependent
refresh, filters, drill-down, reload, layout and conditional visibility.
Selectors, expected values, request URLs, navigation and timeouts require review;
no guessed production DOM bindings or automatic sign-in. Save/Edit and cleanup
are prohibited. Browser/network checks are not a browser-wide no-write sandbox.

The optional `browser` extra provides Playwright. UI assertions compare reviewed
expectations, not automatically fetched API results. Query evidence, browser
evidence and full ARM/Content Hub acceptance remain separate. Existing
`workbook-ui-import` accepts explicitly reviewed external captures; it does not
launch a browser. Live browser execution needs separate exact-scope approval.

Public Graph beta metadata exposes `security/workbooks` and the security
workbook `name`/open `content` model. It does not establish write permissions,
create/update ID semantics or provider acceptance. Retain the ARM candidate
route until those are verified; a future direct-API smoke test cannot replace
full V3.1 package acceptance.

#### Optional explicitly approved Advanced Hunting read validation

Authoring may perform read-only Defender XDR Advanced Hunting query/schema
validation when the author explicitly configures a tenant on the Authoring
run and approves its exact current plan. This is a separate, one-run read
capability, not Qualification: it does not require or discover a workspace,
change the active workspace, run Sentinel source queries, or authorize any
write. Select the run explicitly, inspect `plan-runtime-query-consent`, and
affirmatively approve only `defenderXdrQueryFamily` through
`review-runtime-query-consent` before invoking `validate-advanced-hunting`.

The authorization binds the exact selected run, tenant, Graph client/auth
binding, and every current Advanced Hunting query identity/hash. It is not
reusable across runs or solutions. Dispatch requires an existing cached Graph
credential bound to that tenant; consent never authorizes sign-in or
permission changes. Current query execution and returned-schema checks remain
mandatory. Missing, declined, stale, or incomplete consent/authentication
blocks dispatch. This route cannot satisfy Qualification's source/runtime,
target, consent, dispatch, completeness, schema, packaging, deployment, or
parity gates; source SDK validation remains Qualification-only.

#### Dependency provenance validation

Conversion is always offline. Each XDR YAML requires
`contentProvenance.requiredWorkloads` and `requiredDataConnectors` record arrays.
Structural validation checks the workload vocabulary and record shape;
unresolved `dependencyReviewRequired` records block validation.
The legacy `conversion.requiredWorkloads` labels are not deployment dependencies.

The `sentinel-xdr-dependency-helper` skill may help users fill and review these
records from a Log Analytics lab in either profile. This optional validation
capability requires fresh explicit read-only approval for the exact original
queries and selected tenant/subscription/workspace. It does not reinterpret
Authoring Advanced Hunting consent, select Qualification, or broaden SDK,
deployment, authentication, ingestion, or parity authorization.
Prefer an advertised official Triage capability supporting input metadata;
otherwise use the approved REST read route. Request
`Prefer: include-dataSources=true`. The offline `dependency-plan` importer
checks exact current query hashes and workspace binding before comparing YAML.
Use API input metadata for 1-10 distinct tables, otherwise a recorded
conservative scanner fallback after a successful query. Failures and partial
results remain failures. Unknown tables/connectors require user input.

Keep dependency arrays in authored provenance; do not add the deployment
package/content identity quartet to YAML. V3.1 packaging and actual Graph
deployment resolve that quartet from package metadata and canonical content
identity/version. Only full Content Hub registration includes dependencies.
Preserve disabled status, source content and classification.

#### Workbook dependency review

For a workbook gap, show each query/picker pointer and exact hash, source evidence,
proposed data types, workload/connector mappings, and unresolved technical issues.
Offer static/manual review or separately approved bounded lab metadata discovery
in either profile. Acceptance, changes, and deferrals are explicit and hash-bound;
batch acceptance must retain individual query records. Static suggestions are not
automatically reviewed facts. Query errors, partial failures, stale evidence,
unknown functions, and unsupported providers remain blockers after acceptance.
Parameterized lab queries need approved concrete bindings, not unresolved workbook
tokens or an invented time range. Source metadata is not output-schema lineage or
proof that a connector is installed.

When reviewed connector alternatives are equivalent for the declared requirement,
recommend the modern connector over a deprecated route, citing recommendation or
lifecycle evidence. Do not require both merely because both appear in the solution.

Preserve explicitly reviewed Sentinel workspace function invocations for workbooks
and AH queries; this support does not apply to Custom Detections. Standard
built-in ASIM parsers starting with `_` (such as `_ASim_*` and `_Im_*`) are
accepted by Defender XDR Advanced Hunting and can be used in both Custom
Detections and Defender Workbooks; do not reject them as unsupported
workspace-saved functions. Bind required
functions to packaged definition paths, aliases, and current file hashes in
`contentProvenance.requiredWorkspaceFunctions`. Resolve underlying tables separately.
Treat `_GetWatchlist` as a supported built-in, not a missing workspace parser,
an installation prerequisite, or an AH function-support blocker.
Keep `Watchlist` platform-reference inputs in raw lineage, but omit them from
telemetry data types in required workload/connector records. They are not fed
by a data connector and must not cause connector-discovery prompts.
During V3.1 packaging, required parser installation is unconditional and the outer
workbook installer depends on the actual saved-search resources in the enclosing
template. Content registration is not installation; deployment order is not AH
visibility or runtime acceptance evidence.

Reviewed optional vendor branches may be absent with visible warnings and incomplete
coverage. Offer keep/remove/defer; removal requires a scoped parser-change preview,
explicit approval, current definition evidence and fresh validation. Never silently
remove shared parser resources or treat missing branches as confirmed no telemetry.
Accepting a removal request does not itself establish that the function was edited.

#### Optional resumable full-inventory authoring

The CLI also provides a separate, explicit `--yolo` mode for durable local
full-inventory authoring. It requires a newly initialized run and an explicit
`authoring` or `qualification` profile; it never upgrades a legacy run. The
run-scoped contract freezes the complete recursive source-rule inventory,
including source and query hashes, and records per-rule conversion and
validation results. It reuses existing discovery, full-solution conversion,
and structural validation. It does not call runtime providers, package, deploy,
ingest, create a PR, or change the review/qualification gates.

Select and record the exact run ID returned by initialization for all later
commands; do not infer a run from timestamps:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --version-bump none `
  --yolo

sentinel-xdr-migration workflow-yolo `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"
sentinel-xdr-migration workflow-yolo-refresh `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump none
```

Refresh imports only existing provider reports with matching persisted query
hashes; it does not execute queries. The complete frozen inventory remains the
coverage denominator, including unprocessed, blocked, and suppressed rules.
`E` counts each rule with an unresolved error or suppressed disposition once;
shared provider failures are accounted separately. A stop is persisted when
more than 50% of the inventory is in `E` and cannot be cleared by improved
later results. The 80% migrated threshold is advisory only. It does not replace the separate
partial-publication rule below. Stale source/target hashes or
changed inventory stop processing rather than overwriting user content. See the toolkit README's
[YOLO authoring guide](../README.md#opt-in-full-inventory-yolo-authoring) for
the contract, exact coverage definitions, and evidence-export option.

For a YOLO run, `package-v3-1` uses the existing workflow state: validation
must pass and every rule in the complete inventory must clear technical and
explicit-review gates. It records fresh V3.1 report and artifact hashes; the
advisory coverage threshold never bypasses these gates. The initialization-
selected bump or target-version action is consumed once. A retry may use `--version-bump none`
only after that action was consumed and the current package-input hash matches
the post-build identity recorded by the run. Changed inputs make the previous
package stale and require an explicit new release choice. Every retry runs V3.1
again; an old report, package artifact, or V4 report is never relabeled as
current V3.1 evidence.

The same freshness rule applies to ordinary gated authoring and Qualification
runs. `workflow-status` reports `packageFreshness`; `workflow-next` points back
to packaging and sets `releaseActionRequired` when package inputs or artifacts
are stale. Status reads are read-only. After completing the normal conversion
and validation gates, explicitly select a new release action for the exact
current input identity, then package using that same action:

```powershell
sentinel-xdr-migration workflow-plan-package-release `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump patch `
  --expected-package-input-sha256 "<current-package-input-sha256>"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump patch
```

Choose `patch`, `minor`, or `major` explicitly; no action is inferred. The
expected hash must match current package inputs at selection time. A subsequent
input change invalidates that selection and requires a new explicit decision.
The selected action can be consumed only once for those inputs. If V3.1 fails
after consuming the version, retry with `--version-bump none` only when the
post-build input identity still matches. The old V3.1 report and all package
artifacts are retained as historical evidence before rebuilding. This lifecycle
does not waive technical or entity-review gates: unresolved `reviewRequired`
flags continue to block packaging.

If the initial version action produced an unaccepted candidate and no successful
package exists, changed inputs can use this same explicit new-release command.
The old candidate report must still match its consumed attempt and artifact
hashes. Planning retains that failed action and attempt in release history and
archives the candidate report and package artifacts without accepting them.
Fresh validation and a current applied package selection (or the existing
eligible offline Authoring evidence) are still required. Missing or stale
conversion, runtime, target, or review evidence must be repaired through the
normal workflow first. Unchanged inputs remain a `--version-bump none` retry;
running candidates cannot be replaced. A new candidate must repeat official
validation, ARM validation, consent and acceptance gates. No prior candidate
receipt or approval is copied into current success evidence.

An author may select a canonical target version instead of a patch/minor/major
bump. The target must satisfy `>=3.2.0` and `<4.0.0` and need not be consecutive
with the current version. For example, an initial release may go directly from
`3.0.7` to `3.2.1`:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --version-bump none `
  --target-version 3.2.1

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --version-bump none `
  --target-version 3.2.1
```

For changed package inputs, plan the exact target against the current input
hash with `workflow-plan-package-release --target-version <version>` and pass
that same target to `package-v3-1`. The V3.1 backend persists the approved
target in solution data and metadata. If the target was written before a build
failure, a retry must omit `--target-version` and use `--version-bump none`;
it is permitted only for the matching post-write input identity. A target
cannot be combined with a non-`none` bump. The persisted target/action and
release plan retain the same review, freshness, campaign, and one-time
consumption protections as bump actions.

The resulting solution release must be `>=3.2.0` and `<4.0.0` for V3.1
packaging, including no-bump rebuilds and pipeline-calculated versions.
An older source version is not silently promoted; select a supported target or
bump explicitly. Independent content-version checks remain unchanged.

For offline Authoring only, if the successful package is already at the
approved version but its release-note row is missing, use
`workflow-plan-release-notes-refresh` rather than selecting another version
bump. Supply the exact approved date, change-history cell, and current package
input hash. The planner requires current offline validation and a successful,
fresh V3.1 receipt, records the complete input-file hash manifest, and archives
the prior package evidence. Add the exact resulting row immediately below the
ReleaseNotes table separator, then run `package-v3-1 --version-bump none`.
The required three header labels and their order are matched after trimming
Markdown cell padding; the original aligned header and existing history bytes
are preserved.
Before and after V3.1, the gate permits only that one exact ReleaseNotes change;
any other changed or missing input, stale receipt, mismatched row, or changed
inventory blocks the build. The build creates new package evidence without
changing or consuming another version bump. This route does not apply to
Qualification and cannot replace its runtime, target, consent, or deployment
gates. If the old receipt is stale or does not match the current full input
tree, use the ordinary explicit new-release path instead.

For an explicitly approved non-ReleaseNotes content correction that must retain
the already packaged solution version, Authoring may use
`workflow-plan-same-version-content-rebuild` instead of selecting another
release. It requires the exact current package-input hash, the actual solution
matching the successful V3.1 receipt from the selected run, and fresh passed
full-inventory offline conversion, structural, and review evidence. List the
exact changed non-ReleaseNotes package inputs with repeated `--changed-input`
arguments. The planner archives the prior V3.1 receipt and artifacts plus a
hash-verified snapshot of the current inputs; the build then uses only
`package-v3-1 --version-bump none` with no target version.

If V3.1 consumed the selected version action but failed before writing a
successful receipt, the same planner can authorize a distinct
`same-version-failed-candidate-rebuild` action. This requires
`--failed-candidate-evidence` pointing to the selected run's persisted V3.1
failure handoff and `--legacy-baseline-evidence` reconstructing the complete
pre-repair input manifest from the failed attempt's exact aggregate hash and
file count. The candidate handoff, consumed failed attempt, generated artifact
hashes, and archived candidate outputs must all match the selected workflow
state. A failed attempt is not a successful package receipt; no success status
or package report is synthesized. If the full prior manifest cannot be
reconstructed exactly, stop rather than infer paths from the approved list.

Both routes are Authoring-only, preserve the same solution version, and do not
relax Qualification runtime, target, consent, or deployment gates. The planner
archives the verified baseline and current input snapshot. Only
`package-v3-1 --version-bump none` with no target version may run. A failed
build may be retried only against the still-pending plan and identical input
manifest; the actual V3.1 build and fresh receipt remain mandatory.

Successful V3.1 receipts include the complete post-build package-input
file/hash manifest. The rebuild planner compares it to the current manifest and
requires the explicitly approved path set to equal the complete additions,
removals, and modifications. Unchanged declarations and every ReleaseNotes
delta are rejected. Dispatch, receipt acceptance, and retries recompute the
same scope and hashes. A legacy receipt without a per-file manifest is rejected
unless `--legacy-baseline-evidence` supplies a comparison whose reconstructed
full prior manifest hashes exactly to that successful receipt; its current
identity and changed-path before/current hashes must also match the plan backup.
The evidence path and digest are saved by new legacy-recovery plans. A
pre-existing legacy plan may provide the same evidence flag to each package
attempt without rewriting its workflow state; if no exact baseline can be
reconstructed, stop rather than infer scope from the approved path list.
`workflow-verify-same-version-content-rebuild --solution <solution> --run-id
<run-id>` performs a read-only scope and receipt check for a pending or completed
rebuild; legacy plans without a saved evidence binding must also supply
`--legacy-baseline-evidence`. For a failed-candidate plan, the saved comparison
evidence and archived failed-attempt artifacts are rechecked; only a later
fresh successful V3.1 receipt can make the completed rebuild verifiable. This
check does not alter workflow state or claim full workflow completion.

#### Evidence-based package selection

When a complete solution run contains item-level runtime or review failures,
maintainers may explicitly package only the artifacts that have current,
hash-bound evidence. This does not change the original conversion manifest,
validation reports, validation-stage status, or authored YAML. It is an
inventory-accounting path, not a waiver: an item is excluded if its structural
validation, source/Graph runtime query, provider/target binding, or required
review evidence is missing, stale, failed, or unresolved. The workflow retains
the full discovery/conversion inventory and reports every included and excluded
Analytic Rule and Custom Detection with hashes, evidence paths, check outcomes,
and reasons. Invalid paths, duplicate references, malformed reports, or other
selection/execution errors block applying the plan.

Use the exact run ID and review the complete plan before applying it:

```powershell
sentinel-xdr-migration package-selection-plan `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"

sentinel-xdr-migration package-selection-apply `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --expected-plan-sha256 "<plan-sha256>"
```

Applying a fresh plan updates only the `Analytic Rules` and `XDR Detections`
selection arrays in `Data/Solution_*.json`; it adds `XDR Detections` only when
the plan explicitly bootstrapped candidates from the complete current
solution-scope conversion manifest. Other metadata, content arrays, and
authored YAML remain unchanged. When the array was absent, planning uses only
manifest output references and records missing outputs; it does not discover
additional candidate files by scanning the XDR folder. An explicitly present
empty array remains an empty selection and is never bootstrapped. In either
case, the complete manifest and current detection files remain accounted for
as included or excluded inventory entries with reasons.

V3.1 consumes only the explicit references written by apply and must not
repopulate excluded detections by scanning their folder. If XDR YAML exists
and no selection plan has added an explicit array, direct V3.1 packaging fails
closed; an explicit empty array means no Custom Detection installation or
registration resources. The plan and apply receipt are rechecked against
current files and evidence immediately before packaging, and package-template
and ZIP contents are checked against the exact plan. Applying snapshots the
original bytes and file identity, rechecks after staging the update, and
performs a post-receipt freshness check. If solution data changes while the
update or a receipt-failure rollback is being prepared, the operation stops
when it detects the change and retains conflict evidence where possible. The
migration writer lock serializes only this tool's own updates; apply requires
that external editors or processes do not modify `Data/Solution_*.json` until
it completes. Filesystem exchange detects changes at the commit boundary but
is not a general compare-and-swap guarantee for writers that do not honor the
lock. A receipt published before a later detected edit is retained as evidence
and is not treated as a valid current selection.

Current local structural validation checks the source rule's kind-specific
contract. Both `Scheduled` and `NRT` rules are supported; scheduling fields
are required for `Scheduled` and forbidden for `NRT`. Historical runtime
evidence is reusable only when its own execution report, provider, current
query hash, run, workflow profile, solution, and target bindings agree. A
current sidecar authorization cannot supply missing execution-report
provenance. Selection reuses matching reports and does not dispatch runtime
queries.

Partial publication is allowed only when validated, unique source-rule IDs
represented by deployable Custom Detections are strictly more than 50% of the
complete original Sentinel Analytic Rule inventory (`2 * validated > original`).
Exactly 50%, fewer, zero, or an empty/invalid denominator is blocked. The
denominator is the full current recursive source inventory, independent of
package selection; a scoped/replaced manifest, omitted source, duplicate
reference, duplicate detection, or source-only Analytic Rule cannot shrink or
inflate the count. A source-only Analytic Rule may remain in the package under
the existing eligibility rules but does not count as a migrated detection.
Only currently structurally valid, explicitly review-resolved, current
source/target/provider-bound query and schema evidence makes a Custom Detection
eligible. Global malformed manifest/report, inventory mismatch, ambiguous
identity, or selection/execution errors remain fatal.

For a non-YOLO workflow, an applied, fresh selection meeting that threshold
may produce a V3.1 package containing only eligible reviewed/validated
selections, with outcome `partial-package-validated`. Preserve every excluded
YAML file and its source failure evidence; report the original denominator,
validated numerator and coverage, selected evidence scope, and every excluded
identity/reason. Do not turn excluded items into placeholder deployables.
Validation remains blocked for the full inventory and its original evidence is
unchanged. Authoring may publish this package without a lab; it must not claim
full-inventory validation.

Qualification may continue for the exact selected subset after that package
passes. Deployment, ingestion, and parity must operate only on the currently
applied selected content and retain every existing per-item runtime/schema,
target, permission, disabled-state, ownership, consent, write-approval,
ingestion, and parity gate. Excluded item failures do not block aggregate
progress for the selected subset, but neither selected-subset completion nor
parity may be represented as full-inventory success. Persist and report the
selection-plan identity and exact selected evidence scope through Qualification.
Changing selection or any bound input invalidates the package/receipt and
requires replanning and renewed exact-scope decisions as applicable. This is
not a waiver of any selected-item gate. YOLO continues to require
full-inventory validation and review success. Reuse only current,
run/target/provider-bound runtime reports; selection does not rerun queries or
treat historical query hashes as proof of a current full-file hash.

### Qualification — explicit opt-in

#### Reusable lab read approval

Request one explicit approval for migration-related read operations across all
selected solutions in the same locked lab, rather than separate approvals for
each solution or read-only step. Show the tenant, subscription, resource group,
workspace ARM ID and customer ID, expected provider surfaces, and read-operation
families before recording approval. Include supported status/access checks,
read-only preflight, and source/Advanced Hunting query execution. Query API
requests may use HTTP POST without being resource writes.

Reuse that approval while the lab definition is unchanged and approval has not
been withdrawn. Adding a solution or refreshing its query hashes within the
approved operation families does not require another lab-read approval, but
each dispatch still requires current exact inventories, hashes, target checks,
bounded execution, effective access, and a supported provider route. Record
those bindings with the run's evidence; do not reuse stale validation results.
Reconfirm when any locked lab identifier or confirmed primary-XDR-workspace
setting changes, or when an operation expands beyond the approved read scope.

Interactive authentication, Entra consent, role changes, deployments,
ingestion, rule enablement, deletion, and other environment writes are excluded.
Lab-read approval never grants access or authorizes an unsupported route,
unrelated tenant-wide discovery, secret/token export, or repeated unchanged
failed batches. Local evidence/report refreshes do not require another live-read
approval. Existing CLI consent checks must still be satisfied through supported
commands; reusable user approval is not permission to bypass those checks.

`Discovery -> Conversion -> Validation -> Packaging -> Deployment -> Mock ingestion -> Alert parity -> Report`

This is optional internal or ISV lab testing. Tools and adapters default to
**Authoring** and ask before optional **Qualification** (or **Cancel**). No
Qualification workflow state may be created while Qualification is declined or
cancelled. A configured tenant or workspace does not imply consent.

Qualification requires an approved non-production tenant and workspace plus
one early, plan-bound request for the anticipated conditional validation and
qualification actions, followed by separate exact operation/batch approval
immediately before any environment write begins. The early request is not
authorization to execute writes.

After target lock and before Discovery, build the local scope plan and ask once
for the complete potential-action set. Repeat this request only when the
target, plan identity, included resource families, payload, count caps, or
cleanup ownership changes. Do not ask the same broad planning question again
at later deployment preflight when the bound plan is unchanged.

For the contributor-facing authoring sequence, local configuration, provider
boundaries, review decisions, V3.1 packaging, and pending orchestration
capabilities, follow the toolkit README's
[Contributor authoring guide](../README.md#contributor-authoring-guide).
That guide describes current deterministic CLI behavior separately from
autonomous MCP dispatch, cross-provider research, and interactive decision
experience, which are not implemented by this Python package.

### Solution-local target configuration

Qualification may use a credential-free `Solutions/<solution>/.env`, copied
from the placeholder-only `Tools/SentinelToXDRMigration/.env.example`. Replace
its two literal values, `AZURE_TENANT_ID` and
`SENTINEL_WORKSPACE_RESOURCE_ID`; never put credentials or shell expressions
in this file or real identifiers in the shared example. The strict parser
accepts only those assignments and does not source the file, expand variables,
or execute commands. The solution `.env` is Git-ignored and excluded from
package inputs and optional evidence exports. It is not read by Authoring, and
no global or process-environment target defaults are silently applied.

Inspect the selected solution before approving it:

```powershell
sentinel-xdr-migration doctor --solution "Solutions\<solution>"
```

For a new configured Qualification run, explicitly opt in to Qualification and
confirm the displayed target:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile qualification `
  --confirm-configured-target `
  --version-bump none
```

The workspace subscription is derived from its validated ARM ID. Only after
explicit target confirmation does the resolver verify `az account show` has
the configured tenant and derived active subscription, then issue a single
exact `az resource show --ids <workspace-arm-id>` request for the customer ID.
It never lists or scans workspaces. Authentication or exact-read failures stop
initialization; sign in separately to the approved identity and retry.
Explicit command-line values remain supported, but conflicts with `.env` fail
with an actionable error instead of silently choosing either value. Supplying
both `--tenant-id` and `--workspace-resource-id` is also explicit target
confirmation; the subscription is derived and the customer ID may be resolved
or supplied.

An existing locked Qualification run remains authoritative on resume. Changes
to `.env` cannot retarget it; a conflicting local value blocks resumption and
must use the existing explicit target diagnosis/repair contract. Local `.env`
does not store the derived customer ID; that resolved identity is persisted in
the locked run target after the exact read.

## Initialize or resume

Install the CLI when necessary:

```powershell
python -m pip install -e Tools\SentinelToXDRMigration
```

Run `workflow-status` first. If state does not exist, default to `authoring`
(or confirm whether the user wants optional `qualification`) before
initializing:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "<solution-path>" `
  --workflow-profile authoring `
  --version-bump none
```

For an approved qualification run, use `qualification` and include
the complete locked target. Alternatively, after reviewing the per-solution
configuration above, use `--confirm-configured-target` instead of supplying
tenant/workspace values; the workflow derives the subscription and reads the
customer ID only from that exact approved workspace:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "<solution-path>" `
  --workflow-profile qualification `
  --confirm-configured-target `
  --version-bump "<none-patch-minor-or-major>"
```

Before requesting a workspace value, inspect `doctor`. If
`configuredWorkspaceResourceId` exists, present it for explicit reuse
confirmation. Do not ask the user to retype it. When a new workspace is
approved and resolved, persist it for future solution workflows:

```powershell
sentinel-xdr-migration configure-workspace `
  --tenant-id "<tenant-guid>" `
  --subscription-id "<subscription-guid>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --workspace-customer-id "<workspace-customer-id>"
```

Always resume from persisted state:

```powershell
sentinel-xdr-migration workflow-status --solution "<solution-path>"
sentinel-xdr-migration workflow-next --solution "<solution-path>"
```

Every workflow run stores its reports, configuration, operational state, and logs
under `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/`. New workflows
get collision-safe timestamp/UUID IDs; resuming keeps the same ID. Use
`workflow-runs --solution "<solution-path>"` to list runs and pass
`--run-id "<id>"` to all solution commands when more than one exists.
Never select the newest run heuristically. `workflow-init --new-run` explicitly
creates an isolated workflow rather than resuming; obtain the normal profile
selection first. Content YAML and package files remain shared solution content,
not per-run snapshots.

When workflow context contains a full `workspaceResourceId`, it is authoritative
for the rest of that run. Pass it explicitly to every Azure command and never
list, rediscover, rank, or scan other workspaces. A Log Analytics customer-ID
GUID may be resolved to an ARM resource ID once, then the ARM ID must be
persisted. A tenant mismatch is an authentication blocker for the selected
workspace, not a reason to choose another workspace.

All live stages must load
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json` and
verify the tenant, subscription, workspace ARM ID, and workspace customer ID
before proceeding. Specialist tools must not independently discover or infer
any of them.

If the exact ARM path fails, the orchestrator may run
`qualification-diagnose`. It may make one exact customer-ID query restricted
to the locked subscription. When a unique same-identity correction is found,
show the old and proposed resource IDs and require explicit approval before
running `qualification-repair-target --approve-target-update`. No repair may
change tenant, subscription, or customer ID.

The ignored local file
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\workflow-state.json` records stage status, attempts,
timestamps, artifacts, evidence, profile, workspace, and version action. Never
store credentials or tokens in it and never mark a stage passed without
evidence.

Prior flat solution Logs and legacy `Reports/<solution>/sentinel-xdr-migration` (including the old
`AZURE_SENTINEL_REPORTS_ROOT` override) and report files in `XDR Detections`
are read-only fallback locations. Status reads never move or initialize state.
Before resuming writes, run `migrate-reports --solution "<solution-path>"`,
review the file list, and obtain approval for
`migrate-reports --solution "<solution-path>" --run-id "<preview-run-id>" --apply`.
This copies artifacts into that run, preserves originals, and records their hashes.
Honor any prior flat migration receipt before treating newer flat state as
authoritative over archived root Reports. Never import one run's archived
evidence into a new workflow. Conflicting copies,
changed legacy originals after migration, and missing migrated files block
resumption; reconcile explicitly rather than selecting stale evidence.
Never delete legacy state or initialize a replacement to bypass this gate.

All solution Logs are Git-ignored and excluded from content/package inputs.
The solution-local `.env` target file is separately Git-ignored and excluded
from package/evidence content.
They may contain raw provider responses and lab identifiers, and must not be
force-added to a PR. An optional, explicit local-only PR evidence export is available:

```powershell
sentinel-xdr-migration export-evidence --solution "<solution-path>" --run-id "<run-id>"
```

Run it only after the selected run is stable. It writes trackable
`Evidence/<run-id>/{summary.md,evidence.json}`, never overwrites an existing
snapshot and does not change operational state, rerun tests or perform cloud
writes. No environment-write approval is needed for this explicit local export.
The header identifies the checked public solution name, profile, recorded status,
current observed solution version, requested version action and actual export
time/tool version. Missing target versions and original export times remain
unknown. An explicitly authorized header-only edit of an older snapshot must
preserve its results/hashes and distinguish new header observations from
historical export facts; `export-evidence` still refuses overwrites.
All recorded statuses, including failures, blocks and not-run results, are
preserved through a fixed allowlist; raw provider data/free-text messages and
tenant identifiers are omitted. Missing and unsupported evidence is explicit.
Hashes anchor current local bytes, not trusted attestation or historical test
binding. Review the snapshot before committing; see the toolkit README for
allowlists and filename-sanitization limits. Evidence is never loaded as resume
state or included in solution content inputs or Marketplace ZIPs.
Persisted filesystem references are solution-relative where possible; resolve
them against the selected solution, not the current shell directory.

Start and complete each stage:

```powershell
sentinel-xdr-migration workflow-start-stage `
  --solution "<solution-path>" `
  --stage discovery

sentinel-xdr-migration workflow-complete-stage `
  --solution "<solution-path>" `
  --stage discovery `
  --status passed `
  --message "Reviewed source inventory" `
  --artifact inspection="Logs\sentinel-xdr-migration\<run-id>\inspection.json" `
  --evidence "Analytic Rules\Example.yaml"
```

Allowed terminal statuses are `passed`, `failed`, and `blocked`. Explain
failed and blocked results. Correct and retry only that stage.

### Event-driven durable coordination

An optional local coordinator can track accountable ownership, executor claims,
idempotent events, and durable handoff notifications for an already initialized
run. Enroll using its exact run ID. The coordinator reads the existing
`workflow-status` and `workflow-next` results; it does not create, reorder,
complete, or weaken canonical stages or prerequisites:

```powershell
sentinel-xdr-migration coordinator-enroll `
  --solution "<solution-path>" `
  --run-id "<run-id>" `
  --owner "<accountable-owner>"

sentinel-xdr-migration coordinator-reconcile `
  --solution "<solution-path>" `
  --run-id "<run-id>"
sentinel-xdr-migration coordinator-status `
  --solution "<solution-path>" `
  --run-id "<run-id>"
```

`coordinator-status` performs deterministic reconciliation and persists any
expired-claim, decision, and outbox updates; it is not read-only.

The ignored registry is local to the current checkout. Its owner is independent
of any ephemeral executor. A claim is an atomic reservation, never permission
to run a command. It binds the action, exact current target, prerequisites,
evidence, and (for runtime tasks) query-set hash. An expired claim is blocked as
unknown outcome; cloud requests must not be blindly retried. Record results
through the existing gated CLI first, then post a hash-bound
`coordinator-event --kind executor-completed`. The event does not complete a
stage; reconciliation consumes it only when the authoritative workflow state
or current evidence supports the reported outcome. An expired claim can be
resolved only against the exact current target and evidence hash recorded by
an officially completed stage, through that completion event or
`claim-resolved --outcome completed`; this updates coordinator state only.
Confirming `not-started` requires separate hash-bound owner evidence.
If that terminal stage exposes a same-ID retry with changed evidence, the
retry remains blocked until the previous claim's authoritative handoff is
validated against its retained action snapshot and consumed.

Coordination starts in shadow mode: it persists and reports decisions but
dispatches no CLI commands, authentication, grants, runtime queries, writes, or
user approvals. Changed decisions, including `approval-needed`, create durable
outbox items. `coordinator-event --kind approval-requested` separately records
an exact action, purpose, and target request; an adapter may deliver that
outbox only after rechecking the current action hash and target; reconciliation
supersedes stale outbox items. The explicit `coordinator-ack` means delivery
only, never approval. No host messaging adapter or autonomous daemon is
provided. Use the existing user-confirmation,
approval, preflight, and guarded CLI gates; a confirmation or preflight result
is not proof of service configuration or runtime success.

Optional shared prerequisites are keyed by dependency, purpose, and target
fingerprint; for example, Advanced Hunting (`advancedHunting`) and Custom
Detection (`customDetection`) authorization remain separate even for the same
tenant. A submitted dependency remains an actor-reported, locally hash-checked
assertion; it is not automated permission or service-configuration proof. The
coordinator can show source and Advanced Hunting runtime tasks independently
without changing the single Validation stage gate. Status and
reconciliation report missing owner, ready-idle work, untracked running stages,
expired claims, unconsumed completion handoffs, and pending outbox deliveries.
The watchdog runs only when invoked; it is not a background service.

### Solution watchdog best practice — `ACTION_REQUIRED`

For each solution and current workstream, retain exactly one accountable
watchdog owner bound to the explicit run ID, selected profile, agreed goal, and
current approved scope. A global observer may aggregate status and alerts but
does not replace the solution owner or create duplicate owners. The existing
owner performs watchdog duty; do not launch replacement/nested agents to
re-check the same work. If ownership is missing, escalate to the responsible
parent rather than inventing an owner.

The owner should retain one read-only periodic watch until the agreed goal is
verified complete or explicitly stopped/cancelled. Cadence is explicitly
configurable per coordination instruction rather than a fixed toolkit timer;
the current coordination setting is three minutes. Avoid hot polling,
interrupting a running owner, or launching duplicate executors. A fresh run
retargets the same owner and schedule, preserves prior history, and never
imports or relabels old-run success as current-run evidence. Completion requires the goal-specific
persistent artifact and its bound evidence—not an idle agent, status message,
toolkit commit, or watchdog acknowledgement. Stop the watch after genuine
completion or explicit stop/cancellation.

When progress needs human/parent action, emit a prominent, repeatable
`ACTION_REQUIRED` handoff through the existing agent completion/handoff
channel. Include at least:

- solution, current run ID, agreed goal, and the single watchdog owner;
- the exact next operation or prerequisite and the responsible parent;
- current approval reference and exact scope, or explicitly `missing`;
- readiness evidence and each missing, stale, or blocking prerequisite;
- last **real solution progress** timestamp, elapsed stalled time (or
  `unknown` when it cannot be proved), and a stable outstanding-alert identity.

Raise the alert when an approved operation is ready but has not started, or
when a concrete gate requires parent action. Repeat it on ordinary ticks until
genuine execution/progress, verified completion, explicit revocation, or a
reported blocker resolves it. Another status update, toolkit commit, or
watchdog acknowledgement does not reset the progress timer or clear the alert.
The parent must consume the handoff by executing the already-approved bounded
next step, obtaining a required missing approval, or reporting the exact
blocker; do not wait for the user to repeat the request.

Example (all values are illustrative):

```text
ACTION_REQUIRED
solution=ExampleSolution
runId=20261012T000000Z-example
goal=publish validated partial package (>50% migrated-CD coverage)
watchdogOwner=solution-owner
nextOperation=apply reviewed selection plan and build V3.1 package
responsibleParent=parent-coordinator
approval=granted; reference=approval-ref-01; scope=local-authoring-package-only
readiness=blocked; missing=2 of 3 source rules lack current validated CDs
lastRealProgressAt=2026-10-12T09:00:00Z
elapsedStalled=28 minutes
alertIdentity=ExampleSolution/run/selection-coverage
```

Watchdog ticks are read-only and do not grant build, packaging, toolkit,
content, workflow-state, cloud, authentication, ingestion, enablement, or
deletion authority. Actual operations remain with the existing sole executor
and must use the workflow's separate approvals and exact write gates. Do not
repeat unchanged, already-granted common choices or expand into unapproved
work. The watchdog rule does not add a scheduler, backend, agent registry, or
native CLI watchdog capability.

#### Scheduled status reminders, single-owner execution, and approval forwarding

To improve operator visibility during longer stages or larger batches, use the
read-only status reminder helper (`workflow-status-reminder`). It reads actual
`workflow-state.json` and run artifacts—never inventing progress, completion
estimates, or approvals—and emits `currentActivity`, `expectedNextStep`, a
grounded batch `durationExplanation` (for example, when source Analytic Rules
`>= 15` or workbook queries `>= 50`), a stage `workflowDiagram`, and
`watchdogCoordination` (`readOnlyObserver: true`, `createsExecutor: false`,
`singleOwnerRespected: true`). When the deterministic `stateFingerprint` matches
`status-reminder-cursor.json`, it sets `suppressedNoChange: true` so repetitive
no-change notices are suppressed.

Before candidate packaging/ARM validation preflight, present a concise
lab-deployment preapproval prompt stating the exact inventory scope:
`X Sentinel rules, Y workbooks, and Z custom detections`, with `lab-deployment`
as the default validation route and `arm-ttk` available as an offline Authoring
option.

Maintain single-owner execution and safe approval forwarding with the CLI
helpers:

- `workflow-execution-owner --action claim|release`: records the single
  accountable owner (`ownerId`, `operation`, `scope`, `claimedAtUtc`) in
  `execution-ownership.json` and blocks any duplicate executor
  (`duplicate_executor_blocked`) with a different `ownerId` for the same
  `(runId, operation)`.
- `workflow-forward-approval --action forward|verify`: binds `runId`,
  `operation`, `approvedBy`, `forwardedToOwnerId`, `exactScope`, and
  `approvalSha256` in `forwarded-approvals.json`, rejecting any scope
  broadening, mismatched owner, or altered digest.

## Stage gates

### Discovery

Run `sentinel-xdr-migration inspect`. Account for every source rule, ID, table,
query, and existing XDR artifact. Reject duplicate IDs, ambiguous provenance,
and content without defensible attacker behavior or observable telemetry.

For content-creator Authoring, assume source-referenced Sentinel tables are
expected to be available in XDR; do not ask whether the target resolves both
tables or directory fields. This is not a deployment-environment guarantee.
The tool owns standard schema resolution: use actually advertised official
schema MCP/API capabilities when authorized, or authoritative Microsoft
documentation, with source/target query-surface and table/alias context.
Do not ask customers to choose `Timestamp`/`TimeGenerated` or field casing.
For custom `_CL` tables, infer only from actual available connector, DCR, or
table definitions; distinguish inferred, schema-verified, and runtime-validated
evidence. Missing/conflicting metadata is a tool/evidence limitation, never
permission to fabricate a schema from the suffix.

This is approved authoring policy; the current finite rename catalog is not a
general schema resolver. See the README's
[current-versus-pending capability matrix](../README.md#content-creator-authoring-policy-and-pending-implementation).

### Conversion

Run `sentinel-xdr-migration convert`. The converter must preserve source Analytic
Rules; source-authoring metadata repairs are a separate step described below. Generated
files belong under `XDR Detections`, remain disabled, and contain source
provenance. Pass only with no conflicts and no unresolved `needsReview` item.
Exception: a best-effort entity-mapping assumption that is explicitly marked
`reviewRequired` may continue through conversion, structural validation, and
read-only query/schema testing. Preserve the pending review finding and its
source/query hash binding. This is not a review acceptance and does not clear
other `needsReview` findings, technical errors, failed queries, or malformed
content. Do not pause a complete batch for an assumption-only mapping choice.
The later packaging gate continues to reject unresolved review flags; this
policy does not authorize package readiness, deployment, or parity claims.
Only deployable detection YAML belongs under `XDR Detections`; conversion
manifests, reports, configuration, validation evidence, and state belong under
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>`.

For an explicitly selected pilot, `convert --rule-id "<source-template-guid>"`
limits writes to one rule while retaining global identity/provenance checks.
Pass the locked `--run-id` and reviewed `--config`; use `--overwrite` only for
the reviewed selected draft. Unknown, malformed, duplicated or excluded selected
IDs fail before writes. Unselected drafts, including config exclusions, are
never changed or deleted. The run's manifest/report are replaced with explicit
rule scope, not merged into full-solution coverage. Earlier passed conversion
and downstream stages are blocked with historical evidence retained.
Do not pass solution conversion/validation stages or package from scoped results:
the workflow and toolkit packager reject them. Full-solution conversion and the
normal gates are required before proceeding. Structural validation of existing
files alone is not conversion coverage. This pilot does not introduce scoped
runtime/deployment qualification or a generic waiver. The global source-runtime
missing-schema whitelist is limited to `IdentityInfo` and cannot authorize
scoped conversion, deployment, or reuse of stale query evidence. See the README's
[single-rule CLI contract](../README.md#single-rule-conversion).

Explain entity mapping differences using the restricted target mapping contract:
identify retained identifiers, actual lost information, and query-proven
equivalence separately. An unsupported FullName property is not automatically
identity loss. Existing source SID joins are not migration regressions unless
conversion changes their semantics. The README includes a
[concrete Local Admin Group Changes review](../README.md#worked-review-local-admin-group-changes).
Source `requiredDataConnectors` is preserved in optional top-level XDR authoring
metadata, outside deployment `properties`, with exact presence/empty-list and
extensible-entry fidelity. On initial discovery, malformed metadata is a
conversion/structural failure, not a silently dropped declaration or a final
authoring outcome. Older artifacts require an
explicit conversion refresh; no automatic rewrite or gate waiver is implied.
See [dependency preservation](../README.md#connector-dependency-preservation-and-deployment-boundary).
Target registration/dependency translation remains pending design; do not add
an undocumented field to Graph or inner detection-rule properties.

When an entity identifier cannot be preserved equivalently in the final
entity mappings, retain its available query output value **in addition** as
an `alertTemplate.customDetails` column binding. This applies to explicit
mapping overrides as well as automatic conversion. When static output binding
is proven, report this specific mismatch as nonblocking information. Missing or
unproven bindings, conflicts, limits, and dropped values remain warnings or
errors. Supplemental evidence does not restore entity identity or correlation.
For an unsupported identifier with an available output column, choose the
best supported target mapping deterministically when possible, retain the
original output value in custom details, and mark the choice as pending review.
For example, `Host.FullName` can provisionally use the documented
`hosts.nameColumn` when no stronger supported Host identifier is available.
State that the mapping is an assumption, not equivalence. This assumption-only
review does not interrupt conversion or read-only query/schema tests; it remains
visible and blocks packaging/deployment until reviewed. Never invent a target
field or query output column, and do not let this exception waive any unrelated
error or review gate.
Preserve source/override custom details, reject conflicting
explicit keys, and use stable collision-safe keys for added details. Record the
source identifier, bound output column and availability status in conversion
provenance. Do not rewrite KQL or emit known projected-out supplemental columns.
Unknown output bindings require runtime schema verification, not an availability
claim. Respect the documented 20-pair limit without truncation and disclose the
4 KB runtime-value limit. See
[supplemental entity evidence](../README.md#supplemental-entity-evidence-in-custom-details).

For a source lookback shorter than a documented native XDR service window,
conversion may constrain event time only after conservative proof of a single
matching native input and its time-column binding. The filter belongs directly
after the table input, before any aggregation; preserve existing predicates.
Record original/effective/service windows, rationale, and late-ingestion risk.
Joins, unions, historical branches, reassigned columns, or ambiguous semantics
remain `needsReview` without speculative query edits. Explain that the event-time
window is constrained to the original Sentinel lookback while the fixed service
windows remain different. This is not cadence or alert-parity proof; generated
transforms still require ordinary runtime validation. Any applied Advanced
Hunting KQL rewrite invalidates earlier query-runtime evidence and blocks
previously passed validation and downstream stages while retaining old reports
as historical. Rerun the complete Sentinel and Advanced Hunting query families
against the exact current queries. Runtime imports must include the SHA-256 of
the exact query executed; missing or mismatched hashes are blocked. Review
decisions are source/query-hash scoped and expire after a rewrite. Failed KQL
results cannot be relabeled as provider gaps, and fallback is only for provider
failure with a complete-family rerun. Zero rows indicate execution, not parity.
Static/unit checks do not promote a transform to runtime-validated.

Preserve **all** source tactics in source order in authored YAML; multiple
tactics alone are not a review gate. Assign flat source techniques only to
compatible tactics using the repository MITRE catalog, retaining independently
recorded original lists. Unknown/invalid classifications still block. Legacy
single-tactic overrides correct techniques only for their existing named source
tactic, with an explicit warning that they neither narrow nor reorder the
source list. Invalid or incompatible overrides fail rather than lose metadata.
Historical single-tactic draft findings require explicit regeneration, not a
mandatory choice of one tactic for authoring. See the
[MITRE contract](../README.md#mitre-authoring-and-deployment-contracts).

#### Metadata repair and user notification

Within approved content-authoring scope, fix unambiguous schema-defined
metadata inconsistencies at **both ends**: the Sentinel source and its generated
XDR draft. This applies to all metadata, not just connector declarations.
The orchestrator performs a minimal source-authoring maintenance edit and then
uses the existing converter to refresh the affected draft; normal conversion
must never automatically edit source rules. No backend auto-repair engine or
toolkit modification is authorized by this content workflow.

Only mechanical, schema-clear corrections are automatic within that scope.
For example, rename a lone AWSS3 `datatypes` key to required `dataTypes`, keeping
`AWSS3` and `AWSVPCFlow` unchanged. Do not normalize arbitrary extension fields,
valid IDs/data-type values, declaration order, duplicates, or absent/empty lists.
Conflicting keys/values, ambiguous intent, tactics/techniques, entity semantics,
identities and versions require an explicit decision, not an invented fix.
Intentional source/target contract differences are not inconsistencies to erase.

Record file scope, field paths, exact before/after values and schema rationale.
Preserve prior report snapshots and query hashes. For an isolated repair, pass
the selected source `--rule-id`, locked `--run-id`, reviewed `--config` and
approved `--overwrite`; never recreate deliberately deleted unselected drafts.
Verify both metadata structures and their correspondence, unchanged queries,
identities, versions and disabled lifecycle, and untouched unrelated files.
Refresh diagnostics with the existing tools and record repair evidence without
waiving stages or representing scoped output as full-solution coverage.

Inform the user of repairs and outstanding findings separately, including the
affected files and before/after values. Metadata repair clears only the resolved
error; runtime checks remain not run if unexecuted, and unrelated mixed-surface
reviews/warnings remain visible. Identify older comparison pages and exported
evidence as historical unless explicitly refreshed; never attach new hashes to
old snapshot content. See the README's
[metadata repair policy](../README.md#repair-metadata-at-both-ends).

### Validation

If the user declines runtime validation, do not authenticate or run live
queries. Present this disclosure while retaining actual static/schema checks:

> KQL has not been validated because this migration runs without runtime validation. Enable full validation, or review/accept the specific migration checks below.

This disclosure is not runtime verification. Report unexecuted checks as not
run; keep failed, blocked, and unresolved-review results visible. A specific
review acceptance is not runtime verification. Offline Authoring may complete
Validation only through its explicit `validationMode=offline-authoring` route:
the current complete recursive source inventory must have fresh full-solution
conversion and structural evidence, all technical findings and hash-bound
review decisions must be resolved, and no persisted runtime report may be
overridden or discarded. This outcome records `runtimeStatus=not-run`, clearly
states that Sentinel and Advanced Hunting runtime validation did not run, and
is not runtime/XDR qualification. It does not dispatch queries or weaken any
Qualification gate. If any prerequisite is missing or stale, or actual runtime
failure evidence exists, keep Validation blocked and preserve that evidence.
If a current provider report is recorded after offline Validation passed, the
workflow reopens Validation and downstream gates so the new evidence is
evaluated rather than silently ignored. Do not turn an unmet runtime check
into an environment-only error.

For a legacy Authoring run whose passed Conversion stage lacks
`manifestSha256`, use the explicit
`workflow-recover-conversion-evidence --solution <solution> --run-id <run-id>`
operation. It binds only the selected run's existing `manifest.json` after
revalidating current complete inventory, clean conversion outcomes, target
provenance, review resolution, and full-solution structure. It never repairs an
existing mismatched digest or accepts a scoped/stale manifest. Do not edit
workflow state manually or reconvert to bypass a failed recovery. Once
recovered, resume the already-running Validation stage, or start it if still
pending, then complete it with `runtimeStatus=not-run` and
`validationMode=offline-authoring`.

Run structural validation. When runtime validation is authorized, validate
original Sentinel and converted Advanced Hunting queries. Prefer capabilities
actually advertised by the official Sentinel Triage MCP; do not invent tool
names. Verify the exact persisted workspace/tenant and read permissions before
live queries. For the Graph Advanced Hunting family, execute each exact
converted detection query only; do not add table, function, or schema probes.
The runtime plan and consent inventory must contain the same one-to-one
detection-query set. If a provider-level failure interrupts a query family,
rerun the entire family through the native Azure Monitor Query SDK for Sentinel
(`validate-sentinel-sdk`) or Microsoft Graph for Advanced Hunting, and record
the provider gap with complete-family evidence. The SDK uses the selected
Qualification run's locked workspace and current Azure CLI identity, sends the
exact source KQL as a request value, and does not impose a separate timespan.
It verifies the active CLI tenant and subscription against the locked target
before querying, then pins AzureCliCredential to the locked tenant only; it
does not pass `--subscription` to token acquisition because Azure CLI rejects
combining it with `--tenant`, and it never changes the active account.
Never mix providers within one family, and never fall back on a real KQL
semantic/runtime error. The legacy `log-analytics-cli` import remains
supported for externally executed evidence.
Keep structural, runtime, schema-binding, and qualification results separate.
`runtime-validation.graph.json` binds every result to the SHA-256 of the exact
Advanced Hunting query. Imported Sentinel MCP or Log Analytics results must
carry `querySha256` for the exact persisted source query; the SDK runner binds
it automatically and `record-runtime-validation` blocks missing or stale
bindings. A validation stage can pass as runtime
validated only with complete current-hash Sentinel and Advanced Hunting reports.
Authoring may explicitly record `runtimeStatus=environment-blocked` when no
current exact-query KQL/runtime failure exists; this is not runtime
qualification. Qualification cannot use that exception.

The validation-stage producer records the canonical `sentinelRuntimeJson`
reference and the legacy `sentinelRuntimeReport` alias for the exact source
report. Consumers accept either reference only when every present reference
resolves to that same report; conflicting, stale, or unsafe references are
rejected. A missing reference may be repaired only by the guarded
`Tools/ignored/repair-runtime-report-references.py` maintenance utility after
it independently verifies the passed stage, complete source and Graph
families, typed SDK schemas, query hashes, and report-owned run/target/
consent/dispatch bindings. Its default is read-only dry run; `--apply` changes
only the canonical state reference under the workflow writer lock and records
a preimage backup and receipt. This reference normalization is not validation,
does not clear failures or review gates, and never upgrades legacy reports
whose own execution provenance is missing. A stale or failed validation stage
is not eligible.

The source-runtime missing-schema whitelist is global across solutions, source
queries, and runs, and contains exactly `IdentityInfo` (case-insensitive
matching; canonical report name `IdentityInfo`). It automatically classifies
only a current Sentinel/Log Analytics source result with HTTP 400,
`failureKind=query`, and `SEM0100` explicitly stating that the `IdentityInfo`
table could not be resolved. This includes the preserved Azure Monitor SDK
error structure/message (`'summarize' operator: Failed to resolve table or
column expression named 'IdentityInfo'`) and the equivalent explicit
`Failed to resolve table 'IdentityInfo'` wording already present in provider
evidence. A missing column, another table, mixed/multiple error codes or
diagnostics, partial family/provider failure, authentication/authorization,
tenant, transport, timeout, stale query hash, or changed inventory is not
whitelisted. The classifier is structure-aware and source-provider-only.

There is no per-run allowlist, actor, reason, or acceptance command. The
derived runtime assessment is bound to each exact current source-query hash
and the complete source family. It does not create or mutate a decision
artifact: the raw source result remains `failed`, with its original provider
error. A qualifying result is represented as `source-waived`, never passed,
successful, or executed, and reports include both the whitelist table/reason
and the unchanged raw failure.

The whitelist only classifies source missing-table failures. Validation may
complete as `runtimeStatus=source-waived` only when every other current source
query passes, every converted XDR query has exact successful execution and
actual output-schema evidence (including verified `customDetails` bindings),
and full-solution structural, technical, and review gates pass. Direct stage
completion enforces those gates independently. A source-waived query alone
never completes Validation when XDR is unrun, has missing schema, or any
unrelated gate remains. Whitelist status remains visible in reports while the
overall Validation stage is blocked. No XDR schema, mapping review,
technical validation, packaging, deployment, ingestion, or parity gate is
weakened. Documentation that `IdentityInfo` exists in Advanced Hunting does
not establish availability in a selected Sentinel source workspace.

When investigating table/schema uncertainty, use standard-table documentation,
provider query schemas, and solution-owned parser or custom connector DCR/table
metadata. Do not invent schema or defer tool-owned repository/provider research
to the customer. Present scoped evidence and proposed assumptions for explicit
user accept/reject; stale source or query evidence requires re-review.

Unavailable workload tables are blocked environment results. Zero rows prove
query execution, not behavioral parity. Entity mappings require review.
For custom-detail bindings, verify the target output schema even when zero
rows are returned. Imported successful runtime results must include the actual
target-query `schema` array when custom details exist; a column count alone
cannot prove bindings. Runtime value size remains unverified by schema alone.

Defender Advanced Hunting and Log Analytics workspace queries are distinct
surfaces. A table visible in one does not prove availability in the other.
Always name the failing surface and use only the persisted workspace for
Sentinel validation.

For Authoring, structural success with an environment-only runtime gap may
complete this stage as passed with `runtimeStatus=environment-blocked`; preserve
the exact error and do not claim runtime qualification. This allows V3.1 package
creation. Qualification keeps the same gap blocking because deployment, mock
ingestion, and parity require the selected lab environment.

### Packaging

Use V3.1 for solutions containing XDR Detections:

```powershell
sentinel-xdr-migration package-v3-1 `
  --solution ".\Solutions\<solution>" `
  --version-bump none
```

When the solution worktree does not contain the current V3.1 tooling, select
the approved toolkit checkout explicitly. The solution remains the source and
output root; the selected toolkit supplies the entry point, helpers, templates,
and validation contract. Omit `--toolkit-root` for the existing same-repository
behavior:

```powershell
sentinel-xdr-migration package-v3-1 `
  --solution "<solution-worktree>\Solutions\<solution>" `
  --toolkit-root "<toolkit-worktree>" `
  --run-id "<run-id>" `
  --version-bump none
```

V3 is the legacy Sentinel-only packager and intentionally skips XDR
Detections. Use `none` for repeat checks. Use an approved `patch`, `minor`, or
`major` action once when preparing the submission package; it synchronizes the
solution data and metadata versions.

Require the generated template, UI definition, parameter file, versioned ZIP,
AR/CD count matching, correct `E5Flavor` conditions, disabled CDs, unique IDs,
and explained validation results. Complete the packaging stage only with
`packager=V3.1`, the generated `packaging.v3_1.json`, and its template, UI,
parameters, and ZIP paths. Existing package files are not current-run evidence.
Do not relabel historical V4 evidence. Rebuild with V3.1. XDR detections and
Defender Workbooks require customer usage attribution: a missing `trackingId`
triggers published Marketplace lookup even with offline skip controls.
Lookup failure or ambiguity stops packaging before artifact output without
changing metadata. Verify the offer identity or supply the complete Partner
Center ID unchanged in SolutionMetadata.json; never synthesize it.
Optional-attribution packages retain offline skips and warning-only failures.
V3.1 copies only the first authored tactic and its compatible nested techniques
into the ARM payload, without changing the complete YAML/provenance. Disclose
this intentional classification loss; packaging is not classification/alert
parity validation and must not mark parity passed.

Offline Authoring may use this package gate only after its explicit
`validationMode=offline-authoring` Validation stage has passed for the current
full inventory. If initialization selected `version-bump=none` but a first
versioned release is required, inspect the current package-input SHA-256 and
explicitly plan one `patch`, `minor`, or `major` action against that exact hash
before invoking V3.1. Do not reuse stale selection, skip review gates, or
consume a second version action. Detection-bearing Qualification still requires
its exact runtime-bound selection before packaging. The versioned workbook
route described above requires workbook query/UI evidence after installation,
before final Qualification completion.

### Advance deployment-scope planning and consent

In Qualification, produce and review a deterministic, local deployment-scope
plan immediately after target lock and before Discovery. This is the single
advance-consent request for the anticipated conditional qualification plan.
Refresh and display it during later preflight, but do not re-ask for unchanged
scope. The plan binds to the explicitly selected Qualification run and its locked
`qualification-target.json`; it does not read a new target, authenticate,
discover resources, or call Azure. The solution-local `.env` is only an input
to the existing target resolver. It is not authentication, consent, or a
retargeting mechanism, and it is excluded from source/package fingerprints.

`preflight-deployment` exposes additive `deploymentPlanning` metadata. To
persist the standalone plan and obtain its current `planSha256`, use:

```powershell
sentinel-xdr-migration plan-deployment `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"
```

This command is local-only and writes `deployment-scope-plan.json` under the
selected run. Review the exact target, manifest-declared content counts and
workflow identities alongside raw source-file counts and unlisted files,
current reviewed disabled drafts, recursively unique source-rule identities,
eligible maximum additional Custom Detections, exclusions, content/package
hashes, component resource types, package selections, ingestion payload plan,
and scope caps. For playbooks, distinguish manifest-declared deployment
templates from actual Logic Apps workflow resources; parameterized names in
different templates are separate workflow resources. The plan distinguishes
ineligible new-conversion candidates
from matching current reviewed drafts: a candidate-generation limitation does
not invalidate a current reviewed draft whose persisted disabled Graph payload
and explicit projection validate. The eligible maximum is an upper bound, not
a promise that every rule converts or is deployable.
If there is no current package or reviewed ingestion plan, the affected plan
portions remain provisional. Unknown counts, costs,
retention, schemas, payloads, routes, or resources do not become blanket
approval.

Planning consent is an explicit, separate local decision. It is bound to the
current `planSha256`, exact locked target, selected component resource types,
included resource families, count caps, and package resource inventory. Record
the complete selected component set only after reviewing the plan:

```powershell
sentinel-xdr-migration review-deployment-plan `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --expected-plan-sha256 "<planSha256-from-plan-deployment>" `
  --actor "<reviewer>" `
  --approve-component sentinelAlertRules `
  --approve-component xdrCustomDetections `
  --max-additional-custom-detections <reviewed-cap>
```

At the initial request, present the complete action inventory for this exact
target and plan before showing the suggested default selection:

| Potential action group | Scope to show before asking |
| --- | --- |
| Disabled Sentinel AR / Graph CD creation or approved updates | Exact source-rule IDs and reviewed drafts; separate AR, CD, and pair counts; additional-CD cap; rules remain disabled. |
| Conditional fallback DCR and DCE creation | Exact contract, stream, destination, and candidate IDs/types; only if no compatible existing solution DCR is proven; DCE only if selected or required. |
| Conditional custom-log table creation | Exact table/schema/path/column count; only if the contract proves the table absent. Never alter an incompatible existing table. |
| Mock telemetry ingestion | Shared payload hash, record/batch counts, destination/table, stream, marker/timestamps, schema/transform/contract hashes, estimated bytes/cost/retention; ingest once per AR/CD pair, benign controls separate. |
| Controlled alert parity | Exact pair IDs/count, proposed test window, enable/restore operation bounds, and completion/abort plan to restore both rules disabled. |
| Full-package installation and XDR registration | Current package identity/resource inventory and every selected package flag; distinguish installation/registration from package creation. |
| Explicitly owned cleanup/deletion | Exact resources, ownership evidence, deletion cap, and exclusions; pre-existing or unowned resources are never included. |

Present a structured consent form with **Approve the broadest currently
bounded and available scope** preselected as the suggested default, alongside
**Select components**, **Revise the plan**, and **Decline advance consent**.
The preselection is only a proposal: it is not consent and must not write a
consent record. Show every proposed component, cap, target, resource family,
and package flag explicitly before submission. Require an affirmative user
submission/confirmation of the displayed scope; a preselected choice without
submission, a cancelled/closed form, a decline, or no response records no
approval. A user may narrow, revise, or decline the proposal.

“Broadest currently bounded and available” means only components the current
consent CLI supports and the current plan can bind to complete evidence. When
both routes are available, the suggested set may include the disabled
Sentinel-AR/Graph-CD pair and separate later `fullPackageAcceptance`. For the
package component, display every exact current package selection flag and its
proposed boolean value; when the plan exposes five flags and all-true is a
valid bounded selection, show all five names individually with `true`, never
hide them behind an “all” label. Do not silently add conditional DCR/DCE,
custom-table creation, ingestion, parity, or cleanup: include such a component
only when its scope is complete, supported, and explicitly shown as selected.
Unknown, provisional, unsupported, or unselected components remain
unapproved; if the broadest scope cannot be completely bound, preselect only
the largest valid bounded subset and list excluded groups with reasons.

Persist only the exact, affirmatively submitted component and flag selection
after checking it against the current plan. The proposed default alone,
environment state, or an absent/cancelled response must never set consent to
approved. Denial or absence must not block independent read-only checks or
offline Authoring.

Sentinel alert rules and Graph Custom Detections are a pair-first route and
must be approved together, disabled, with an explicit cap no larger than the
current eligible maximum. A later `fullPackageAcceptance` component is
separate and requires a current verified V3.1 package plus explicit values
for every current package selection flag. It covers full-package installation
and selected XDR installation/Content Hub registration, not just package
creation. Pair-first deployment and later package acceptance are distinct
routes; package files are not live deployments. Stored playbook, workbook,
connector, API, or connection definitions do not imply live instantiation or
enablement.

The current consent CLI supports only the component names documented below.
The planner reports `controlledAlertParity` as provisional with eligible pair
IDs and calculated enable/restore request bounds, but cannot persist parity
consent until a finite test window and complete batch fixture plan are bound.
`ownedResourceCleanup` is unsupported: no exact run-owned deletion inventory
or deletion executor exists. Neither category can be approved through
`review-deployment-plan`; do not invent component names or claim these actions
are preapproved. An earlier approval limited to DCR/DCE does not approve
ingestion, enablement, package acceptance, or cleanup.

Separate components are available for `mockTelemetryIngestion`,
`fallbackDcr`, `fallbackDce`, and `customTableCreate`. Ingestion approval
requires a reviewed run-bound payload and exact destination/stream, records,
batches, payload and schema/transform/contract hashes, marker/timestamps,
estimated bytes/cost, and retention impact. The same reviewed payload is
ingested once per AR/CD pair; benign controls remain separate. DCR/DCE are
conditional provisioning scopes supporting ingestion of locally generated
mocks; they are not required to generate mocks. DCE requires an explicit
selection and must be paired with the DCR component. A DCR fallback is
conditional on no compatible existing solution DCR being proven. The current
resolver checks registered exact resource-name candidates only; it does not
discover arbitrary solution-owned DCRs, so this limitation must remain
visible and an exact fresh check is still required before provisioning.

Custom-table creation is conditional only when the exact supported ingestion
contract proves the selected custom-log table absent and supplies its schema,
path, columns, and plan. A present incompatible table is blocked, not altered.
An existing compatible native table such as `CommonSecurityLog` means table
creation is not needed; never create a custom lookalike. Ingestion, table
creation, DCR/DCE provisioning, rule deployment, enablement, cleanup,
retention changes, role assignments, and identity/app-registration changes
remain distinct operation scopes. Planning consent does not authorize any of
them.

Consent is never inferred from absent/false/unknown metadata, workflow
continuation, a token or role grant, environment identity, example counts,
mock-generation hypotheses, or package selection. Changes to the locked
target, plan/content/package hashes, resource families, payload, selected
flags, or count caps require a fresh plan and renewed consent. Do not hand-edit
workflow state to simulate a review. Planning-consent denial or absence must
not block independent read-only checks or offline Authoring.

Separate the advance request from authentication, Entra admin consent,
permissions, role assignments, and resource-write approval. Identity and
access steps never imply resource consent. A changed target, resource family,
mode, payload, cap, package flags, or cleanup-ownership boundary invalidates
advance consent and requires a refreshed plan and explicit renewed selection.

Advance consent is not final execution approval. Immediately before each
bounded environment-write operation or batch, show its operation, locked
tenant/subscription/resource group/workspace, solution/version, exact
resources, actions/methods and count, plus current permission/readiness
evidence, and obtain explicit approval. One approval can cover the enumerated
batch; it need not be repeated for each underlying HTTP request. Pause for
approval if a write expands beyond the approved batch. Planning consent cannot
substitute for final approval, permissions, technical readiness, or deployment
evidence.

### Deployment — qualification only

Repeat deployment of the same reviewed detection identities to the same locked,
approved non-production lab is a supported, bounded create-or-update workflow;
do not add a separate mandatory “check whether each AR/CD already exists”
pre-step. Keep all rules disabled. The Sentinel route sends `PUT` to the
deterministic `Microsoft.SecurityInsights/alertRules/{source-rule-id}` resource,
which idempotently creates or updates that alert rule for the same ID and
payload. The alert-rule-template API is a catalog read surface, not a resource
this direct-deployment command creates; the `alertRuleTemplateName` field links
the deployed alert rule to its source template. Any package `contentTemplates`
installation is a separate package-acceptance route with its own explicit scope
and approval.

For Graph, the current deployer derives the stable client-provided ID
`xdr-<source-rule-GUID>`, performs an exact-ID `GET`, uses `POST` only when
that ID returns 404, and uses `PATCH` when it returns 200, followed by required
read-back verification. Treat this supported CLI sequence as a repeatable
workflow-level upsert for the reviewed ID, not as a guarantee that arbitrary
Graph `POST` requests are idempotent. The separate pre-deployment
`preflight-deployment` exact-rule existence/readability check is optional
diagnostic evidence; it is not proof of ownership, readiness, or permission.
However, the current Graph deployer still requires its own exact-ID `GET`, and
the current preflight also performs exact-ID reads and can report them as
blocking. Documentation alone cannot skip those backend reads. Do not bypass
them with a direct `POST`, blindly retry a write with an ambiguous outcome, or
overwrite an ID whose ownership/content is uncertain; stop and require
maintainer review for that collision or read-access limitation.

Only repeat this workflow against the explicitly approved, locked lab with
reviewed identities/content, the exact-scope write approval immediately before
the operation, required permissions, and the existing disabled-state and
post-deployment verification gates. Repeatability does not authorize writes to
production, unrelated resources, or enabled content, and it does not waive
review of unexpected existing IDs.

Deploy every reviewed AR and CD disabled. Verify Azure RBAC and Microsoft Graph
scopes separately. A successful write without live read verification is
blocked, not passed. Never infer Azure resource permissions from Entra Global
Administrator.
The Microsoft Graph payload builder explicitly projects a multi-tactic authored
detection to its first tactic and retains that tactic's nested techniques.
Eligibility must come from validating this actual disabled Graph payload, not
from a stale authored-document readiness flag. Preserve source YAML and
provenance, and disclose omitted tactics/techniques with classification parity
not established. This API-payload projection is not permission to rewrite the
authored detection or claim semantic parity; package acceptance remains a
separate route and its live behavior requires deployment/readback evidence.

For package acceptance, use ARM validation or preview only where the resource
types and deployment features support it. Bicep extensibility imports do not
support `what-if` ([Microsoft Learn: unsupported deployment
features](https://learn.microsoft.com/en-us/graph/templates/limitations#unsupported-deployment-features));
do not pass or wait for a `what-if` result for that route. An ordinary ARM
preview cannot prove extension acceptance, and ARM template validation must
not be represented as validating extension behavior. The approved actual
deployment followed by readback remains required.

#### Post-validation ARM template deployment acceptance-only step

This optional step is separate from pair-first deployment, verified
full-package installation, alert activation, and alert parity. Run it only in
Qualification after creating the final V3.1 package and passing the repository
build-and-validate script. For each exact solution/run member, collect its
`build-and-validate-report.md` in validation-only mode, against the current
V3.1 package report:

```powershell
pwsh .script/local-validation/build-and-validate.ps1 `
  -SolutionName "<solution-folder>" `
  -ContentRoot "<content-repository-root>" `
  -SkipPackaging `
  -PackageReportPath "Logs/sentinel-xdr-migration/<run-id>/packaging.v3_1.json" `
  -VersionBump none `
  -ValidationSkip ""
```

The runner emits `build-and-validate-binding.json` beside that report. It binds
the final package report/run and artifact hashes, package inputs and
`Package/` fingerprints before and after validation, successful validator
results, selected solution, and `ContentRoot`. The producer records
`sourcePathSemantics` only when the complete source-input fingerprint matches
the package report under POSIX or Windows Python `Path` ordering; the
acceptance consumer honors that recorded ordering across hosts. `Package/`
fingerprints keep their separate ordinal ordering. Windows ordering lowercases
each component before ordinal component comparison, matching `PureWindowsPath`
rather than .NET `OrdinalIgnoreCase` string ordering. Missing, ambiguous,
unmatched, stale, or changed inputs fail closed. The earlier migration
`stages.validation` status is not a substitute. This acceptance-only
readiness is not gated on mock ingestion, DCR readiness, or parity.

Plan the exact same-PR/lab workstream batch, then review its hash, locked
target, parameters, and every selected solution before the immediate
write-approval command:

```powershell
sentinel-xdr-migration plan-arm-template-acceptance-batch `
  --member "<solution-path-1>::<run-id-1>" `
  --validation-receipt "<solution-1-build-and-validate-report.md>" `
  --member "<solution-path-2>::<run-id-2>" `
  --validation-receipt "<solution-2-build-and-validate-report.md>" `
  --shared-decisions "<shared-pr-lab-decisions.json>"

sentinel-xdr-migration deploy-arm-template-acceptance-batch `
  --member "<solution-path-1>::<run-id-1>" `
  --validation-receipt "<solution-1-build-and-validate-report.md>" `
  --member "<solution-path-2>::<run-id-2>" `
  --validation-receipt "<solution-2-build-and-validate-report.md>" `
  --shared-decisions "<shared-pr-lab-decisions.json>" `
  --expected-batch-plan-sha256 "<batchPlanSha256>" `
  --actor "<approver>" `
  --confirm-exact-scope-write "I approve the exact enumerated ARM template deployment acceptance batch"
```

Repeat both member and receipt arguments, in the same order, for each
approved solution. The reviewed batch must match the user-confirmed shared PR
and lab decision. Deployment submits the exact approved V3.1
`Package/mainTemplate.json` bytes through Azure CLI's documented
resource-group ARM route in Incremental mode, supplying the locked workspace
and every package-declared `Deploy*` content flag explicitly as `true`.
Undeclared flags are never invented. The executor binds the exact template
snapshot, parameters, package identity and batch to immediate approval,
persists write intent before submission, and records the deployment identity
and outcome. A per-member durable reservation blocks blind resubmission after
an ambiguous attempt, including when a later invocation reorders the batch.
One batch approval covers only its enumerated members; it does not authorize
an expanded batch.

For this acceptance-only receipt, require only recorded terminal ARM
`provisioningState: Succeeded` for each member. Do not require `what-if`,
resource-group resource reads, per-resource read-back, or behavioral tests
for this result. `Failed`, nonterminal, missing-state, timed-out, or partial
outcomes remain durable failure/unknown evidence and must be reconciled, not
blindly retried. ARM `Succeeded` is deployment-submission acceptance only: it
does not prove MicrosoftSecurity import behavior, exact content installation
or read-back, activation of disabled detections, alert parity, or completed
Qualification. Incremental mode does not guarantee no impact. Keep verified
installation, post-install activation, and optional parity as separate gates.

### Mock ingestion — qualification only

Use `sentinel-solution-optional-testing` for this stage:

1. Run read-only workspace, DCR, Sentinel query, and permission preflight before
   fixture preparation or ingestion. Report telemetry-write permission, DCR
   creation permission, conditional DCE creation permission, and conditional
   destination-table creation permission separately. Check DCE creation only
   when the selected route includes a DCE. This diagnostic preflight does not
   provision resources or grant write approval. An `unknown` or pending-review
   permission is not a grant. Missing write permission blocks the
   corresponding write, not independent read-only workspace, DCR, schema, or
   query checks. This preflight requires no fixture. Pass `--run-id` when the
   solution has multiple runs; omit it only when the run is unique.

   ```powershell
   sentinel-xdr-migration preflight-deployment `
     --solution "Solutions\<solution>" `
     --auth-method azure-cli `
     --run-id "<run-id>"
   ```

   It writes `qualification-dcr-preflight.json` under the selected run's
   `Logs/sentinel-xdr-migration/<run-id>/` and adds
   `dcrPermissionPreflight` to the top-level Graph report. A permission
   `ready` means effective permissions were inspected, not that ingestion or
   query validation succeeded; the preflight never authorizes a write. See the
   README's [preflight report contract](../README.md#qualification-mock-ingestion-dcr-selection)
   for fields and status values. Aggregate `blocked` identifies locked-target
   artifact or mismatch failures; resource-read status `unavailable` includes
   HTTP 401. The per-contract `resourceFingerprint` hashes the exact target,
   candidate DCE/DCR/table IDs, returned resource configuration/schema, and
   current resource states. `contractFingerprint` is the SHA-256 of the
   registered serialized contract; provenance is
   `registered-contract-resolver`, and candidate selection is
   `exact-contract-resource-names-only`. `resourceReadAccess` may be `ready`,
   `denied`, `unknown`, or `unavailable`; `targetVerification` may be
   `blocked`, `unavailable`, `confirmed`, or `not-checked`.
2. Present Continue, Retry permission check, or Cancel. Continue is not write
   approval.
3. Check the default rule-specific `mock.json` path first.
4. Reuse a complete reviewed scenario or invoke
   `sentinel-solution-mock-data-generation`.
5. Require reviewed input for joins, thresholds, aggregation, sequences,
   historical baselines, watchlists, anomalies, and absence-of-data behavior.
6. Prefer a DCR explicitly listed or referenced by the selected solution only
   when its deployed resource in the locked workspace is proven compatible
   with the exact shared fixture, public input stream, transform, destination
   table/schema, endpoint, and permissions. A packaged ARM reference alone is
   not proof that the resource exists. Do not confuse an internal DCR
   identifier with its public input-stream name or enumerate other
   workspaces. For Logs Ingestion API fallback, structured records must use a
   customer-authored `Custom-*` input stream and `transformKql` to map to a
   supported `Microsoft-*` output. Public table schema does not reveal a
   connector's internal parser or enrichment, and reserved/service-managed
   columns must not be assumed writable. If no solution-listed DCR is suitable,
   a supported contract may be used to author a separate, isolated DCR locally
   and provision it only in the approved non-production Qualification target
   after exact-scope approval. A DCE is needed for private-link ingestion or
   when the DCR has no ingestion endpoint; this repository's contract tool may
   provision an isolated DCE as part of its route, but DCE creation is not a
   universal API requirement. “Locally” means locally authored configuration,
   not a local ingestion service. Never modify an existing connector DCR or
   redirect a native table to a custom lookalike; use a documented native
   telemetry generator or block the test when no supported ingestion path
   exists. See the README's
   [DCR-selection policy](../README.md#qualification-mock-ingestion-dcr-selection).
7. Require separate exact-scope approval immediately before ingestion or
   provisioning any new DCR, any DCE included in the selected route, or table.
8. Group compatible rules by source table and supported ingestion path, then
   ingest each shared `mock.json` exactly once.
9. Track ingestion acceptance and query visibility independently.
10. Run the exact AR and CD queries over the same unique scenario markers and
   require identical matching source-row keys before alert parity.

**Implementation status:** The solution-first DCR preference is the intended
policy, but the current registered-contract resolver checks contract-specific
resources in the locked target and does not yet discover or prefer a
solution-referenced DCR. Do not claim automatic solution-DCR selection; report
only compatibility and permission results actually established by the
available preflight and resolver.

Each AR/CD pair owns one shared `mock.json`; separate AR and CD payloads are
prohibited. `mock.json` may contain multiple correlated records when the
detection requires them. Never create a recurring ingestion job, and never
redirect an unsupported native table to a custom lookalike table. Use a
documented native telemetry generator or mark the rule blocked.

Every payload needs a unique scenario marker and expected malicious match-key
set. Pass only after ingestion is accepted and both exact queries observe the
same marked records. The existing alert-parity stage then compares alerts from
that same one-time ingestion.

For supported Standard tables, the scenario generator writes
`ingestion-contract.yaml` from the reviewed registry under
`Tools\AzureMonitorLogsIngestion\contracts`. Apply the locked workspace at
runtime:

```powershell
azure-monitor-logs-ingestion run `
  --contract "<scenario-folder>\ingestion-contract.yaml" `
  --workspace "<locked-workspace-arm-id>" `
  --payload "<scenario-folder>\mock.json" `
  --report "<versioned-report-path>"
```

The connected agent must execute generation, provisioning, ingestion,
visibility checks, exact row parity, alert parity, evidence updates, and
cleanup as one user-facing operation. Do not hand intermediate commands or
path discovery back to the user.

### Alert parity — qualification only

Use `start-alert-parity-batch` with a plan covering every converted detection:

1. Verify all ARs and CDs are disabled.
2. Enable all reviewed pairs.
3. Reuse the already ingested shared `mock.json` records; do not ingest a
   second AR- or CD-specific payload.
4. Capture alerts for every pair.
5. Compare counts, match keys, severity, tactics, entities, decisive evidence,
   and benign controls.
6. Complete or abort so every rule is disabled after success or failure.

### Report

Run `sentinel-xdr-migration solution-report`. The JSON and HTML reports must
distinguish passes, review requirements, environment blocks, skipped checks,
and genuine failures.

## Safety and completion

- Never use production telemetry or a production workspace for qualification.
- Ask before interactive authentication.
- Do not bypass failed or blocked gates.
- Do not rerun a passed release packaging stage and increment twice.
- Keep detections disabled except during controlled parity.
- Authoring completes after packaging and reporting pass.
- Qualification completes only after all optional lab stages and reporting
  pass.
