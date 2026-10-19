# Microsoft Sentinel to Defender XDR migration toolkit

This toolkit converts Microsoft Sentinel analytic rules into versioned Defender
XDR Custom Detection YAML files and provides offline workbook conversion with
candidate V3.1 Defender Workbook packaging.

See [tracked follow-up areas](FOLLOW_UPS.md) for curated capability and
operator-experience work that may be considered separately.

## Package architecture (`solution_manager`)

Implementation modules live under `Tools/SentinelToXDRMigration/solution_manager/`
organized by Solution Manager capability, with `sentinel_xdr_migration` retained
as a backwards-compatible package alias:

- `solution_manager/cli.py` — Unified CLI router (`solution-manager` / `sentinel-xdr-migration`)
- `solution_manager/core/` — Shared workflow state, coordination, onboarding, preflight, target context, budgets, and artifact paths
- `solution_manager/authoring/` — Offline content authoring contracts, schema validation, and dependency/workbook publication rules
- `solution_manager/migration/` — Sentinel-to-Defender-XDR analytic rule and workbook translation engine (including `_workbook_core/`)
- `solution_manager/qualification/` — Live lab deployment, runtime query validation, DCR readiness, Graph/ARM acceptance, and alert parity
- `solution_manager/packaging/` — V3.1 hybrid solution packaging, content selection, and release notes helpers
- `solution_manager/reporting/` — Public evidence projection, HTML dashboards, and reviewer exports
- `solution_manager/research/` — Scaffold for threat-, vulnerability-, and coverage-gap-driven content creation

## Product goal and operator flow

**Product goal:** Allow autonomous migration of Sentinel solutions to Defender
XDR solutions at scale and with quality. Once a user defines the solution, the
toolkit should prepare the best-supported migration candidate, run the
applicable automated checks, and clearly surface assumptions and evidence for
human review. For optional Qualification, the user must also define an approved
non-production test environment and provide the required permissions. Legacy
offline Authoring does not require a test environment. New CLI runs
default to the versioned lab ARM-validation route described below.

The intended operator flow is:

1. **Define scope and mode.** Supply the solution definition and account for
   every source object. Explicitly select `authoring` or `qualification`;
   environment configuration does not implicitly select Qualification.
2. **Prepare candidates in a batch.** Prefer stable, evidence-supported
   mappings. When semantics are uncertain but a defensible target candidate
   exists, generate that candidate without pausing for a per-rule decision,
   preserve the original available values in details where the target mapping
   cannot carry them, and record the assumption, evidence, and source/query
   hashes for review. Do not invent logic, fields, or equivalence.
3. **Check and classify results.** Run structural validation and only the
   read-only query or schema checks supported by the selected mode and
   available authorization. Distinguish reviewable mapping uncertainty from
   malformed input, unsupported structure, missing prerequisites, and actual
   execution or validation errors; the latter remain errors, not assumptions.
   If a source rule cannot be represented as a valid deployable XDR detection,
   retain an explicit diagnostic candidate and disposition outside deployable
   detection YAML rather than fabricate a runnable rule.
4. **Review the batch.** Present complete inventory coverage and per-object
   outcomes, including unresolved, unsupported, unprocessed, and explicitly
   excluded objects. At a later human-review stage, the operator can accept the
   reviewed candidate bundle for packaging, request a scoped change, or exclude
   an object with a reason. Acceptance resolves only the reviewed assumptions
   in scope; it cannot waive technical, input, or query failures. Preserve
   exclusions in the inventory and provenance; a change must regenerate
   affected output and rerun checks against current input hashes. Acceptance is
   a review decision, not proof of runtime correctness or alert parity.
5. **Package and, only if approved, qualify.** Build the package from the
   reviewed, current candidate inputs through the V3.1 route. Packaging,
   deployment readiness, and runtime qualification remain separate. Deployment
   requires explicit approval under the selected versioned ARM route; ingestion
   remains Qualification-only. Neither candidate generation nor review acceptance
   authorizes environment writes.

**Implementation status:** This is the desired product direction, not a claim
that end-to-end autonomous semantic mapping, general uncertainty handling,
batch accept/change/exclude decisions, or candidate diagnostics are already
implemented. Current conversion supports only specific deterministic
best-effort entity mappings with hash-bound `reviewRequired` findings.
Unresolved review and technical gates still block packaging. Existing commands
do not yet provide the general batch-review decisions described above; see
the capability matrix below for implemented behavior and pending work.

## Dependency provenance

Conversion remains offline. Generated YAML declares telemetry prerequisites in
`contentProvenance.requiredWorkloads` (`workload`, `dataTypes`) and
`contentProvenance.requiredDataConnectors` (`connectorId`, `dataTypes`), preserving
the separate source/conversion records and source connector metadata.
Offline validation requires these fields and rejects unresolved
`dependencyReviewRequired` records. Workloads use the toolkit vocabulary
`mde`, `mdo`, `mdi`, `mda`, `mdc`, `entraid`, `purview`, `appgovernance`,
`sentinel`, `mtp`; this is not a claimed public Microsoft enum.

Use the `sentinel-xdr-dependency-helper` skill for explicitly approved
lab-assisted review in either profile. `dependency-plan --solution <path>`
proposes records without network access or YAML writes. Import a complete,
successful, workspace/query-bound metadata family using
`--results <file> --workspace-id <approved-workspace-id>`. The source-validation
SDK requests `Prefer: include-dataSources=true` and compares returned underlying
tables with YAML. It retains its existing Qualification execution/consent gates.
1-10 distinct tables use API metadata; successful missing metadata or more than
10 tables uses the conservative scanner. Query/partial/provider failures are
never empty-success fallbacks. Unknown dependencies require user review.
Tables added by the converted query are also included through a separate
offline reference scan. Source API lineage is not Graph input-lineage evidence.
Shared `SecurityAlert` never establishes a specific connector or Defender
product by itself. Returned output `tables` are not input lineage.

Packaging and actual Graph deployment stamp the four resolved identity/version
keys, without adding them to authored YAML. V3.1 installation and stored
installation templates carry the same lightweight record; the Content Hub
registration additionally contains the authored dependency arrays. Direct
Graph deployment obtains real package identity from solution Data/Metadata and
requires matching provenance on readback. Unbound Graph payload helpers are
planning-only. Offline emission does not prove live Graph/Content Hub support
for this candidate contract. Reviewed YAML dependency edits invalidate package
evidence; reconversion preserves declarations only while source/target queries
and source connector metadata remain unchanged.

## Defender Workbook candidate contract

Workbook support retains the complete `Notebook/1.0` document under
`XDR Workbooks/<relative-source-path>.json`. Source `Workbooks/` files are not
rewritten. Authored `xdrMetadata` distinguishes the canonical content GUID from
the stable installation GUID; its content version inherits the selected solution
release. The Notebook format version and original source metadata version remain
separate.

The authored `xdrMetadata.displayName` prefers a nonempty source
`metadata.name`. If absent, conversion uses the repository
`Workbooks/WorkbooksMetadata.json` title matched by `templateRelativePath`
(including the catalog's filename-only convention); a filename fallback is
retained when the catalog or a matching entry is unavailable. Ambiguous catalog
matches and malformed catalogs fail with an actionable error rather than
choosing an arbitrary title.

`sentinel_xdr_migration.workbooks` exposes `inventory_workbooks`,
`convert_workbooks`, `validate_workbooks`, and `selected_workbook_files`.
Conversion is offline. Reviewed resolution records bind each original query
JSON pointer to its exact raw query hash, complete source tables, and evidence.
Unknown dependencies, unreviewed saved functions, unsupported providers, stale
resolution, and unresolved review findings remain blockers. The converter records all
source items in `workbooks-manifest.json`, separate from detection `manifest.json`.
Queries removed as proven scope-only helpers remain in provenance.

The KQL rewriter treats `Type` conservatively: literal `Type` labels explicitly
projected by a query are retained, and a bare `Type` grouping in a one-line
`let Alias = NativeTable | summarize ... by ...` can be preserved by adding
that table's name as a `Type` value before aggregation. Other `Type` references
remain review findings; they are not replaced with `ActionType` or removed.

Workbook dependency review also recognizes source-free literal `datatable`
queries limited to literal cells, direct `project` expressions, and `order by`.
Complete `range Column from Start to Stop step Step` queries are also recognized
when all three operands are signed 64-bit integer literals or finite real
literals (decimal/exponent notation), the step is nonzero, and its direction
matches the endpoints (equal endpoints are allowed). Range keywords are lowercase;
the column must be a plain ASCII identifier. No range functions, parameters,
arithmetic, casts, comments, additional statements, or pipeline/union tails are
accepted by this exception. The original query is preserved unchanged.
These literal queries require an explicit hash-bound review decision but no
telemetry table, workload, or connector prerequisite; other table-free KQL remains
unresolved. V3.1 prerequisite scanning already treats the range operator as built-in
and continues discovering function calls and telemetry branches in larger queries.
This static exception does not verify runtime visibility or parity. The identity
mappings for `MessageEvents`, `MessageUrlInfo`, `MessagePostDeliveryEvents`, and
`FileMaliciousContentInfo` are grounded in their Microsoft Learn Advanced
Hunting table references; they do not assert runtime visibility or add a schema
where none is catalogued.

The explicit solution Data `XDR Workbooks` array selects deployable content.
An empty array selects none; packaging never repopulates it by scanning files.
V3.1 emits workbook installation and Content Hub registration together under
`DeployDefenderWorkbook=false`, independent of Sentinel `DeployWorkbook`.
Deployment copies omit authored `xdrMetadata` and carry exactly the four resolved
package/content identity and version keys. Full registration also retains
`requiredWorkloads` and `requiredDataConnectors`. Layout and ARM-looking literals
are preserved; literal escaping applies only to package copies.

### Workbook gap review and workspace functions

Create a read-only proposal with
`workbook-dependency-plan --solution <path> --run-id <run-id>`.
The JSON plan carries `planSha256`, complete source/query inventory, connector
alternatives, and function candidates. Optional `--results <metadata-file>
--workspace-id <approved-workspace-id>` imports approved lab evidence; planning
and import never execute queries or authenticate.

Connector selections in solution Data accept `Data Connectors/<file>` and,
when the solution directory is directly under `Solutions`, the exact
`Solutions/<current-solution-directory>/Data Connectors/<file>` repository-relative
form. Plans return solution-relative POSIX `sourcePath` values for both forms;
source Data selections are never rewritten. References must name existing files
within the current solution's `Data Connectors` directory. Other solutions,
absolute paths, backslashes, empty/dot/traversal segments, and symlinks are
rejected. Review regenerates the same canonical plan and checks connector hashes,
while retaining the hash of the original solution Data.

Apply explicit decisions with `workbook-review --solution <path> --run-id <run-id>
--plan <plan-file> --decisions <decision-file> --plan-sha256 <hash> --actor <reviewer>
--reference <review-reference> --output-dir <new-run-local-directory>`.
The review emits supported conversion configuration and a review receipt, not
source workbook or parser edits. Use the emitted configuration with `convert`.
`convert --overwrite-workbooks` replaces only unchanged, hash-bound managed
workbook drafts; it never authorizes overwriting existing detections. The
ordinary `--overwrite` option remains a separate, explicit content decision.

Present dependency gaps before asking for acceptance: show the workbook,
query/picker JSON pointer, exact query hash, proposed data types, evidence,
workload mappings, connector alternatives, and remaining technical failures.
Offer static/manual review or explicitly approved lab discovery in either
Authoring or Qualification. Static scanner proposals are not accepted evidence.
Lab metadata identifies underlying inputs, not output columns or installed
connectors. Parameterized queries need explicit bindings before execution;
never send unresolved workbook placeholders or silently choose a time range.

The reviewer can accept, change, or defer each proposal. Preserve separate
per-query records even when identical proposals are accepted as a batch.
Changed query templates or prerequisite definitions invalidate prior reviews.
Deferral leaves a gap unresolved; acceptance cannot waive query errors,
unsupported providers, incomplete source evidence, or runtime/UI gates.

Where reviewed connector alternatives satisfy the same requirement, prefer
the modern connector over a deprecated route. Cite authoritative recommendation
or lifecycle evidence; do not infer deprecation from a connector's name, require
both alternatives by default, or claim that a selected connector is installed.

[Sentinel workspace functions are supported in Advanced Hunting and workbooks](https://learn.microsoft.com/defender-xdr/advanced-hunting-custom-functions#custom-functions-imported-from-microsoft-sentinel-log-analytics),
but not in Custom Detection rules. Preserve reviewed function invocations
instead of requiring inlining solely because the source is a workspace function.
Authored `contentProvenance.requiredWorkspaceFunctions` records bind each
`functionAlias` to its packaged `sourcePath` and exact `sourceSha256`.
Function aliases are not table names: underlying source data types require
separate evidence. The connected workspace, access, nested dependencies,
external data, and exact parameterized execution remain runtime concerns.
`_GetWatchlist` is a supported Sentinel built-in available in AH, not a custom
parser to install or an unsupported-function gap. Preserve its calls and
review underlying data inputs separately; only actual execution/data failures
are findings.
`Watchlist` is platform reference data, not connector-fed telemetry. Retain it
in raw source-lineage evidence when present, but do not propose a workload or
connector telemetry requirement for it or ask the user to install a connector.
This exemption does not hide unrelated unknown data types or actual query errors.

Distinguish required functions from reviewed optional vendor branches. A missing
optional fuzzy-union branch can leave the query usable but its coverage incomplete.
Keep warnings visible; unavailable branches are not verified zero-event results.
Offer keep, remove, or defer. A removal request requires an explicit parser-change
preview and fresh review/validation; it must not silently delete shared parser
resources, unrelated branches, or panels. Catalog joins may reintroduce removed
products and need coordinated changes.

V3.1 installs required workspace parsers unconditionally and orders workbook
installation after their actual `Microsoft.OperationalInsights/workspaces/savedSearches`
resources in the same enclosing ARM template. Parser content-template registration
alone is not installation. Missing, stale, ambiguous, or conditional required
resources block packaging. Full workbook registration retains function prerequisites;
the installed notebook retains only the identity/version quartet. ARM ordering
does not establish AH propagation, query correctness, or provider/UI acceptance.

The V3.1 prerequisite scanner excludes a source query only when current source
file/query hashes and its JSON pointer prove it belongs to a removable scope
parameter, and the target no longer contains or references that helper. A
`removed-scope-helper` status alone is insufficient; retained helpers and
non-helper `resources` queries still block. Source and target scanning use the
shared workbook mapping catalog and reviewed scalar `Granularity` and
`union withsource=Table (print ...)` contracts. Real saved aliases and dynamic
`table()`/`totable()` sources still require review or remain blockers.

**Provider contract unverified:** generated templates and successful local tests
are candidate evidence, not accepted installation or publication evidence.
Independent, approved lab installation, registration/provenance readback, repeat
installation, and update evidence are required for contract acceptance. ARM
success alone does not establish those checks or workbook UI/query correctness.
The known provenance `packageId` ARM-TTK finding remains a failure; no broad
validator waiver or identifier rewrite is applied.

The Microsoft-authored conversion slice is package-local and MIT-licensed.
It has no sibling-checkout, authentication, or live resolver dependency.
`_workbook_core/import-manifest.json` records the imported file hashes and
adaptations. Refreshing this slice is a deliberate maintainer change requiring
reviewed import evidence and the differential workbook fixture tests, not an
automatic runtime fetch.

### Native Defender workbook authoring/import (no Sentinel parent)

Already-native `Notebook/1.0` content has an explicit offline authoring route.
It is **not** migration: no Sentinel sibling, converter replay, conversion
success receipt, workflow-stage receipt or runtime qualification is invented.
Migrated workbooks retain their existing source inventory and deterministic
converter proof unchanged.

Provide the original raw JSON to the plan/review/import commands at
`Workbook Sources/Native/<name>.json` (nested paths are supported). This input
must be available while generating and importing the review, but it need not be
committed, retained in the solution, or copied into the package. Its path and
exact-byte SHA256 remain historical import evidence and preserve the existing
stable identity assignment; validation does not reread or require that source.
The review also binds `canonicalPayloadSha256`: SHA256 of canonical UTF-8 JSON
(sorted keys, compact separators, non-ASCII preserved) for the complete Notebook
after excluding only top-level `xdrMetadata` and `contentProvenance`. This
protects notices, layout, queries, and all other Notebook fields, while strict
query hashes and dependency discovery are independently rechecked. Do not
select the raw source in `Workbooks` or `XDR Workbooks`; it is not a deployment
artifact. The import command creates
`XDR Workbooks/<name>.json` and appends that candidate once to the existing
`Data/Solution_*.json` `XDR Workbooks` selection, preserving other selections
and the solution version. A native-only solution needs no `Workbooks` directory.

Use Python 3.11/3.12 and the toolkit's existing dependencies. For an isolated
toolkit checkout, set `PYTHONPATH` rather than reinstalling an editable package:

```powershell
$Toolkit = 'C:\path\to\Azure-Sentinel'
$Python = 'C:\path\to\venv\Scripts\python.exe'
$env:PYTHONPATH = Join-Path $Toolkit 'Tools\SentinelToXDRMigration'
$env:PYTHONIOENCODING = 'utf-8'
$env:SENTINEL_XDR_PYTHON = $Python
$Solution = 'C:\content\Solutions\Example'
$Source = 'Workbook Sources/Native/example.json'

& $Python -m sentinel_xdr_migration.cli native-workbook-plan `
  --solution $Solution --source $Source |
  Set-Content -LiteralPath '.\native-review.json' -Encoding utf8

# Review/edit native-review.json explicitly; do not auto-accept proposals.
& $Python -m sentinel_xdr_migration.cli native-workbook-review `
  --solution $Solution --source $Source --review '.\native-review.json' |
  Set-Content -LiteralPath '.\native-reviewed.json' -Encoding utf8
& $Python -m sentinel_xdr_migration.cli native-workbook-import `
  --solution $Solution --source $Source --review '.\native-reviewed.json'
& $Python -m sentinel_xdr_migration.cli native-workbook-validate --solution $Solution
```

The plan is the review input, not a success receipt. The review command checks
and echoes complete current decisions; import independently rechecks them.
Neither command auto-accepts proposals. Supply nonempty `actor`,
`reference`, and `displayName`. For **every** current query pointer (including
parameter and nested queries), supply `decision: "accept"` and nonempty
`evidence` describing the exact query's complete input/dependency review.
Keep the proposed `origin`, `source.path`, `source.sha256`, query `path`,
`canonicalPayloadSha256`, `querySha256`, `tables`, `blockers`, `requiredWorkloads`, and
`requiredDataConnectors` unchanged. The native route supports catalogued
non-Sentinel tables and standard built-in underscore ASIM parsers (`_ASim_*`,
`_Im_*`) recognized by the shared workbook classifier, including bare and called
forms. It does not support arbitrary underscore/custom saved functions or
connector/saved-function prerequisites. Reviewers cannot override discovery, label an unknown function
as a table, accept a blocker, or supply arbitrary empty lineage. Unsupported
functions/tables, dynamic/external/cross-resource sources and non-AH providers
require a separate maintainer/content design decision, not a forced import.
Empty table lineage is allowed for recognized built-in ASIM parser queries as
well as the existing strict literal `datatable`/numeric `range` recognizers.
ASIM parser names are not tables: only explicitly discovered catalogued tables
contribute workload records. An ASIM-only query therefore has empty `tables`,
`requiredWorkloads` and `requiredDataConnectors`; these mean no statically
inferred dependencies, not proof of no prerequisites. The toolkit does not infer
hidden parser inputs, workloads or connector coverage, and offline acceptance
does not qualify parser availability or execution in the target tenant.
The plan exits nonzero when it contains technical blockers.

The importer currently produces a legacy review-bearing staging candidate.
Before publication, run `workbook-publication-plan/clean` below: retain that
complete proof locally and publish only this compact native provenance:

```json
{
  "contentProvenance": {
    "format": "public-workbook-v1",
    "origin": "native-xdr",
    "requiredWorkloads": [{"workload": "mdo", "dataTypes": ["EmailEvents"]}],
    "requiredDataConnectors": [],
    "requiredWorkspaceFunctions": []
  }
}
```

There is no public `conversion` or `nativeReview` object. `xdrMetadata` uses the
normal schema/version/display name fields. Canonical UUIDv5 assignment is
`uuid5(NAMESPACE_URL, "native-xdr-workbook:<solution directory name>:<source POSIX path>")`;
the instance is the existing
`uuid5(NAMESPACE_URL, "xdr-workbook-instance:<solution directory name>:<canonical ID>")`.
Relocating a checkout, reimporting, changing query content or changing release
does not change these IDs; renaming the solution directory/source path does.
Import refuses differing existing candidates rather than silently overwriting
them. A deliberate source edit requires a fresh review and removal of the old
local candidate and its `XDR Workbooks` selection before reimport, retaining the
same identity for the same path.

Historical native proof validation compares the **whole original Notebook** with the staging
payload after removing only the two additive authoring fields. Thus query
strings (including CRLF/Unicode), items, notices, tabs and other source keys
remain unchanged. Stale source proof or query coverage, duplicate JSON
keys/IDs/selections, traversal and symlinks fail closed. Native validation is
integrated with `validate_workbooks` and the existing local static XDR adapter.
After cleanup, public structural validation is portable without raw source or
private approval; authoring/package validation requires the current local receipt.
The PowerShell emitter reuses shared Python validation
against its in-memory public document and requires that interpreter's
dependencies; a missing interpreter/dependency is an error, never a waiver.
`SENTINEL_XDR_PYTHON` selects the interpreter; absent it, `python` is used.
The subprocess imports only the emitter's toolkit checkout.

For candidate package regression testing, use the correct V3.1 entry point
from the **content repository root**, with a separate toolkit root, **after
explicit publication cleanup**:

```powershell
Set-Location 'C:\content'
& (Join-Path $Toolkit 'Tools\Create-Azure-Sentinel-Solution\V3\createSolutionV3_1.ps1') `
  -SolutionDataFolderPath (Join-Path $Solution 'Data') `
  -ToolkitRootPath $Toolkit -VersionMode local -VersionBump none `
  -ArmValidationMethod lab-deployment
```

This generates an **unaccepted candidate** with ARM lab validation pending;
it performs no deployment and is not a replacement for production release
validation/acceptance. Do not use legacy `createSolutionV3.ps1`, fabricate an
ARM/ZIP or claim lab/runtime qualification. V3.1 uses the same managed-ID
install/registration contract and default-false `DeployDefenderWorkbook`
switch for native and migrated entries. Installed Notebook provenance remains
only the package/content identity/version quartet; source paths, hashes,
native reviews and authoring metadata are not installed. Registration keeps
the existing reviewed dependency contract. Original Sentinel selections remain
independent and no native source is deployed twice.

### Reviewed post-import workbook corrections (offline)

Use `workbook-update-plan`, `workbook-update-review`, and
`workbook-update-apply` for intentional authored Notebook corrections after
migration/import. These commands do not migrate, deploy, invoke queries, or
establish runtime/UI qualification. They require an explicit original reviewed
**authored** baseline file, for example extracted with `git show` from the
accepted content commit into a review workspace outside deployable content.
Legacy update-reviewed artifacts are not original conversion baselines. A clean
published artifact can instead be the public baseline for a later explicit review.

```powershell
# $Python, $Solution and PYTHONPATH use the same setup as native import above.
$Content = 'XDR Workbooks\example.json'.Replace('\', '/')
$Baseline = 'C:\review-workspace\baseline-example.json'
New-Item -ItemType Directory -Force "$Solution\Logs" | Out-Null
& $Python -m sentinel_xdr_migration.cli workbook-update-plan `
  --solution $Solution --content $Content --baseline $Baseline |
  Set-Content -LiteralPath "$Solution\Logs\update-plan.json" -Encoding utf8
```

Inspect the exact current Notebook and plan, including all current `queries`
with discovered tables/functions and `changedQueries` (added/removed queries
use null previous/current hashes). Explicitly set nonempty `actor` and
`reference`, whole-document `decision: "accept"`, and each changed query's
`decision: "accept"` and nonempty `evidence`. Do not edit generated hashes,
dependencies or the reverse baseline delta. Save under gitignored `Logs` as
`update-decisions.json`; never put review material in authored content or a PR.

```powershell
& $Python -m sentinel_xdr_migration.cli workbook-update-review `
  --solution $Solution --content $Content --baseline $Baseline `
  --review "$Solution\Logs\update-decisions.json" |
  Set-Content -LiteralPath "$Solution\Logs\update-reviewed.json" -Encoding utf8
& $Python -m sentinel_xdr_migration.cli workbook-update-apply `
  --solution $Solution --content $Content --baseline $Baseline `
  --review "$Solution\Logs\update-reviewed.json"
& $Python -m sentinel_xdr_migration.cli native-workbook-validate --solution $Solution
```

Apply preserves the edited Notebook and metadata/IDs, independently validates
the baseline's historical proof, and emits **clean public metadata**, not an
embedded `authoredReview`. It refuses identity/prerequisite changes. Complete
current dependencies are mandatory: native-only lineage, known tables, exact
hash-bound workspace functions, built-in ASIM recognition, and dynamic/cross-
resource rejection remain enforced. Reviewer assertions cannot waive them.

The complete review, baseline bytes, and available historical source bytes
remain in a hash-bound receipt under `Logs\workbook-reviews`. These are local
authoring evidence, not signatures, reviewer-identity proof, runtime qualification,
or publication metadata. Keep external source/baseline evidence; do not delete
it after apply. No duplicate full source Notebook needs to be shipped.

### Clean public workbooks and private authoring receipts

Published authored JSON has only the Notebook, existing `xdrMetadata` identity/
version, and compact `contentProvenance`:

* `format: "public-workbook-v1"` and factual `origin`;
* public `requiredWorkloads`, `requiredDataConnectors`, and
  `requiredWorkspaceFunctions` (including function source paths/hashes).

It contains **no author/reviewer accounts, acceptance decisions, references,
session identifiers, query inventories, conversion receipts, reverse deltas, or
proof histories**. Dependencies are not an acceptance claim. The schema rejects
extra fields in public provenance and prerequisite records. Legacy proof schemas
remain readable for importing/validating old evidence, not for publication.
V3.1 rejects legacy authored files until cleaned; migration/import candidates
must pass the explicit publication step before publishing.

To clean an already reviewed legacy artifact (including old `authoredReview`):

```powershell
$ReviewDirectory = Join-Path $Solution 'Logs\workbook-reviews'
New-Item -ItemType Directory -Force $ReviewDirectory | Out-Null
$Plan = Join-Path $ReviewDirectory 'publication-plan.json'
$Review = Join-Path $ReviewDirectory 'publication-decisions.json'
& $Python -m sentinel_xdr_migration.cli workbook-publication-plan `
  --solution $Solution --content $Content |
  Set-Content -LiteralPath $Plan -Encoding utf8
# Inspect the exact file and complete planned dependencies. Save the plan as
# $Review with explicit nonempty actor/reference and decision "accept".
# Never automatically approve a plan. Do not edit inputSha256.
$Decision = Get-Content -LiteralPath $Review -Raw | ConvertFrom-Json
& $Python -m sentinel_xdr_migration.cli workbook-publication-clean `
  --solution $Solution --content $Content --review $Review `
  --expected-sha256 $Decision.inputSha256
& $Python -m sentinel_xdr_migration.cli workbook-publication-validate `
  --solution $Solution --content $Content --mode authoring
```

Cleanup verifies the original raw SHA and all historical gates before writing,
stores the original artifact/proof **verbatim locally**, and changes only
`contentProvenance`. Notebook settings, KQL, `Notebook/1.0`, content/instance IDs,
and `xdrMetadata.version` remain exact. It does not bump a release. An existing
XDR 3.2.2 or O365 3.2.1 artifact remains at that release; deployment copies use
the selected solution release as `contentVersion`.

Historical hybrid receipts sometimes omitted a nested table. Their limited
same-query historical exception remains usable to validate old proof, but is
**not a public packaging waiver**. The plan adds known missing workloads; it
never invents connector coverage. Reviewers must explicitly supply missing
connector/table prerequisites in the local `dependencies` review. Existing
prerequisites/functions cannot be removed/replaced by cleanup. For example,
an old `SecurityAlert`-only connector record does not establish coverage for
`SecurityIncident`; cleanup blocks until that additional prerequisite is
explicitly reviewed. The historical receipt itself is retained unchanged.

`workbook-publication-validate --mode structural`, the schema, Python
`validate_workbooks`, and the static adapter validate portable public structure/
current source dependencies **without private approvals**. They do not approve
authoring. `--mode authoring`, `native-workbook-validate`, authoring workflow gates,
and normal Python/PowerShell packaging additionally require a current canonical
whole-document hash-bound local receipt. A later query/settings/metadata/
dependency edit needs fresh explicit review; structural success is not a waiver.
The clean/update command creates the receipt that packaging consumes automatically
by current document hash. Prior receipts remain locally available, including when
the same payload receives another authorization.

For an **explicit standalone reproduction**, not authoring acceptance, a clean
public Git checkout can package without private receipts:

```powershell
$env:SENTINEL_XDR_WORKBOOK_PUBLIC_REF = '<published commit SHA>'
try {
  # Use the standalone V3.1 command below, retaining the published release.
} finally {
  Remove-Item Env:\SENTINEL_XDR_WORKBOOK_PUBLIC_REF -ErrorAction SilentlyContinue
}
```

This checks the actual in-memory workbook against the exact file at that Git
commit, plus current public table/function/source dependencies. Missing refs or
edited workbooks fail. There is **no automatic HEAD fallback** and it is not
available as an authoring/workflow approval. Git history/review is the trust
boundary for selecting a published ref; reproduction never claims personal
approval. Receipts/Logs are never ZIP inputs: the package contains the generated
template and UI only. Installed Notebook provenance remains the deployment
identity/version quartet; registration additionally retains public dependencies.

Keep existing version/release and candidate gates: package through
`package-v3-1 --solution $Solution --toolkit-root $Toolkit --version-bump none`
(for an already prepared release), then run the official
`.script\local-validation\build-and-validate.ps1 -SolutionName <name>
-ContentRoot <content checkout> -SkipPackaging -PackageReportPath <exact V3.1 report>`.
That wrapper otherwise defaults to legacy V3 packaging and disallows
cross-checkout packaging; do not use it to create this candidate.
If an old migration run's frozen selection predates the maintained content,
do not alter that run or weaken its selection gate. The existing standalone
content-maintenance backend is:

```powershell
& "$Toolkit\Tools\Create-Azure-Sentinel-Solution\V3\createSolutionV3_1.ps1" `
  -SolutionDataFolderPath "$Solution\Data" -ToolkitRootPath $Toolkit `
  -VersionMode local -VersionBump none `
  -ArmValidationMethod lab-deployment
```

Use the same official validation-only wrapper afterward. This builds a
candidate; it does not establish migration workflow acceptance or lab/runtime
qualification.
Keep automatic attribution lookup and its fail-closed guard; do not add a skip
flag to recover from an attribution failure.

### Toolkit-owner managed update policy

Toolkit-managed Defender Workbooks and XDR detections are updated by stable ID.
Same-ID overwrites are expected, including in the approved lab; a different
existing content hash or version is not an overwrite blocker. Managed workbooks
are intended to be consumed read-only, with personalization in separate copies
using different IDs. Toolkit updates must not overwrite those copies.

This does not waive target/identity binding, effective-access checks, current
candidate evidence, deployment consent, immediate write confirmation or exact
post-write provenance/readback. Detections remain deployed disabled. It neither
authorizes other resources/deletion nor relaxes local source-file safeguards.
Read-only portal/provider enforcement remains something to verify, not a
capability established by this policy. See the
[canonical owner policy](agent-workflows/end-to-end-migration.md#toolkit-owner-policy-managed-same-id-updates).

### Versioned ARM route and workbook QA

New CLI runs persist workbook capability 1 and default to lab ARM validation in
either explicitly selected profile. Authoring can select
`--arm-validation-method arm-ttk`; existing runs retain their scope and method.
Direct library initialization retains legacy defaults unless explicitly opted
in. The [canonical workflow](agent-workflows/end-to-end-migration.md) defines
the versioned candidate, consent and acceptance boundaries.

Static content validation precedes V3.1 candidate generation. A draft cannot
satisfy accepted Packaging. Independent approved ARM and workbook-contract
evidence is required; missing consent or provider support blocks the route,
without fallback or another version increment. Evidence-based metadata preflight
now checks the selected lab, authenticated ARM principal, effective control-plane
access, applicable role/deny assignments, disabled content and exact resource
identities. Unresolved evidence blocks dispatch rather than asserting readiness.
The MicrosoftSecurity extension authentication/write contract remains unverified,
so the current default adapter still blocks Defender workbook deployment.

After `workflow-arm-plan`, use `workflow-arm-preflight-plan` to display the
bounded metadata read operations, then `workflow-arm-preflight-review` with
`--preflight-plan-sha256`, `--actor`, `--reference` and `--decision approved`.
Execute with `workflow-arm-preflight-execute --preflight-plan-sha256 <hash>`;
all commands also require the solution and explicit run ID.
`workflow-arm-preflight-revoke` withdraws that read approval.

Metadata-read approval is separate from deployment consent and immediate write
confirmation. Same-target, same-operation scope can retain read consent across
managed same-ID content updates, but plans and execution evidence must be current.
Changed read URLs, identities or target require renewed approval. The default
reader uses the existing pinned Azure CLI profile and correlates actual ARM
responses with the same bearer. Consent explicitly permits acquisition/refresh
of the scoped ARM token through the existing cached identity, not sign-in, new
credentials, permission grants or Graph/AH token reuse.
Graph extension observations remain explicitly unverified, without borrowing
an Advanced Hunting token. Prior receipts are archived, blocked runs return
nonzero, and these commands never write to the environment.

Workbook-only Qualification records `validationMode=workbook-content` before
candidate generation. Exact query and UI evidence is mandatory before final
Report, not before installation. Mixed solutions preserve detection runtime
prerequisites. Frozen workbook inventory and exclusions never inflate detection
coverage.

Qualification query commands are `workbook-query-plan`, `workbook-query-review`,
`workbook-query-execute` and `workbook-query-revoke`. The reviewed Linux Machines
fixture runs 202 harness queries through independent Sentinel/AH providers with
exact result assertions and no ingestion.

The optional `browser` extra provides Playwright. Provision it with a supported
interpreter and `python -m playwright install chromium` only when requested.
`workbook-ui-plan` additionally accepts a reviewed `--browser-config`, containing
exact DOM assertions, observed tenant/content/instance identities, session/error
guards, request/navigation allowlists, timeouts and viewport. All seven UI check
kinds and their expected values must be reviewed. No production selectors are
supplied or presumed verified.

```bash
sentinel-xdr-migration workbook-ui-review \
  --solution "$SOLUTION" --run-id "$RUN_ID" \
  --plan "$PLAN_PATH" --plan-sha256 "$PLAN_SHA256" \
  --actor "$REVIEWER" --reference "$APPROVAL_REFERENCE" --decision approved

sentinel-xdr-migration workbook-ui-execute \
  --solution "$SOLUTION" --run-id "$RUN_ID" \
  --plan "$PLAN_PATH" --plan-sha256 "$PLAN_SHA256" \
  --storage-state "Logs/sentinel-xdr-migration/$RUN_ID/private/browser-state.json"
```

Plan/input paths are solution-relative; keep private inputs under the selected
run's excluded evidence directory. Session state must already exist, match the
reviewed hash, be user-owned and have no group/other permissions or symlinks.
Ownership enforcement is currently POSIX-only. No automatic authentication,
installation, Save/Edit, permission changes or cleanup occurs. Missing browser
support fails explicitly. Current UI assertions compare reviewed expectations,
not automatically fetched API results. Network classifications are reviewed
attestations, not a browser-wide no-write sandbox.

Receipts under `Logs/sentinel-xdr-migration/<run-id>/workbook-ui.<content-id>.json`
contain sanitized events and hashed observations; failed retries replace current
success and archive previous evidence. No screenshots, raw trace, HAR or session
state are exported. `workbook-ui-import` remains available for reviewed external
captures. Live portal execution still requires separate exact-scope approval.

[Public Graph beta metadata](https://graph.microsoft.com/beta/$metadata) confirms
`security/workbooks` and the `microsoft.graph.security.workbook` model's
`name`/open `content` properties. Write permissions, ID allocation/update
semantics and runtime acceptance remain unverified. Direct Graph deployment
is not implemented; retain ARM until that contract is confirmed. A future
direct-API smoke test will not replace full V3.1 Content Hub acceptance.

## Requirements

- Python 3.11 or 3.12
- PowerShell 7 for V3.1 solution packaging
- Azure CLI for authenticated runtime validation and Qualification

Install the package with a supported Python interpreter:

```powershell
python -m pip install -e Tools\SentinelToXDRMigration
```

The package metadata and CLI enforce the supported Python range. If the active
interpreter is unsupported, select or install Python 3.11/3.12. Do not modify
toolkit source files as an environment workaround during a migration run.

## Offline authoring-contract foundation

`sentinel_xdr_migration.authoring_contract` provides the versioned
`schema/authoring-contract.schema.json` record and offline typed helpers for
validating a complete source-rule inventory, per-rule findings and generated
target hashes, evidence references, qualification state, and separate shared
environment errors. Use `seal_authoring_contract(core_record)` to validate a
core JSON-like record and attach computed summaries;
`validate_authoring_contract(record)` verifies those summaries and returns an
immutable typed record. `calculate_coverage(validated)` returns exact counts,
and `calculate_operation_eligibility(coverage)` returns advisory threshold
signals. References must be repository-relative and hashes must be lowercase
SHA-256. Validation checks reference shape and consistency but does not open,
re-hash, or authenticate the referenced evidence artifacts.

Coverage uses the complete unique inventory as `N`. `M` counts structurally
valid migrated targets with no unresolved rule-specific errors; warnings and
retained mapping assumptions do not reduce it. Blocked, suppressed, and
unprocessed rules remain in `N` and not in `M`; `E` counts affected rules once,
regardless of the number of findings. Shared provider/environment failures
remain separate. The success/PR threshold is tested as `100*M >= 80*N`; the
stop signal is `100*E > 50*N`, without rounding. Qualification counts are
separate: an untested target may count in `M`, while a qualified result needs
runtime-verification and actual-alert-parity evidence. Entity parity records
the value-preservation policy even when entity type, identifier, or custom
field differs. Mapping assumptions and `reviewRequired` are preserved; neither
confidence nor review state grants eligibility.

These are pure, in-memory calculations only. The stop signal does not persist a
stopped workflow or implement autoresume behavior. Threshold results are
advisory and never authorize deployment, packaging, ingestion, PR creation, or
any other environment operation; exact-scope runtime authorization remains a
separate requirement. Parallel orchestration, durable coverage state, gates,
and CLI integration are pending work and are not implemented by this contract.

## Protected implementation

The XDR Solution Manager treats its prompts, skills, migration backends,
packaging backends, schemas, tests, dependency metadata, workflow definitions,
safety gates, and capabilities as read-only during solution migrations.
Runtime, environment, conversion, validation, packaging, or deployment
failures must be reported rather than repaired by changing toolkit source.

The XDR Solution Manager can never perform implementation changes, regardless
of who requests or approves them. Agent and backend development must be done
manually or through a different development agent. The XDR Solution Manager
remains limited to migration artifacts, packaging, validation, Qualification,
and routed reports.

The first milestone intentionally stops before ARM generation. It creates and
validates:

```text
Solutions/<solution>/
  Analytic Rules/
    <rule>.yaml
    Execution/
      <nested-rule>.yml
  XDR Detections/
    <rule>.yaml
    Execution/
      <nested-rule>.yml
  Logs/sentinel-xdr-migration/<run-id>/
    run.json
    workflow-state.json
    manifest.json
```

### Recursive source layout

Discovery includes `.yaml` and `.yml` files (case-insensitive extensions) at
every level of `Analytic Rules`, or the legacy `Analytics Rules` directory.
Conversion preserves each filename and its relative directories under
`XDR Detections`; same-named rules in different folders remain distinct.
Inspection, validation, runtime plans/results, deployment, parity, and reports
use the same recursive inventory. Runtime result `detection` values and parity
selectors use slash-separated paths relative to `XDR Detections`, for example
`Execution/Rule.yaml`. Parity's legacy filename/stem selectors are accepted only
when unambiguous. The shared mock-scenario generator also discovers nested
AR/CD pairs and accepts relative paths; source IDs disambiguate same-named rules.

Persisted manifest results use solution-relative `source`/`output` fields and
portable `sourceRelativePath`/`outputRelativePath` fields.
Use the latter output references in solution data's `XDR Detections` array;
the V3.1 packager already accepts nested paths. Only detection YAML is generated
under `XDR Detections`; reports/configuration remain in ignored solution `Logs`.

Existing flattened or relocated detections identified by source provenance are
reported as conflicts, even with `--overwrite`. Review and explicitly reconcile
or relocate these files before converting; the converter does not silently
duplicate, move, or delete them. Unidentified flat files with a colliding basename
also require review. Symlink content paths and escaping relative references are
rejected. Existing independent XDR release versions and overwrite rules are
unchanged.

Each XDR Detection YAML contains:

- an independent top-level content release `version`, initially `3.1.0`;
- the properties required to generate a
  `Microsoft.Security/detectionRules` resource;
- a disabled-by-default lifecycle state;
- converted KQL;
- optional top-level `requiredDataConnectors`, copied from source authoring
  metadata and never emitted as Graph/ARM detection-rule properties;
- translated entity mappings;
- all source MITRE tactics, in source order, with compatible techniques;
- a `contentProvenance` block linking the detection to its source analytic
  rule and recording conversion warnings.

The YAML contract is defined in
[`schema/xdr-detection.schema.json`](schema/xdr-detection.schema.json).

### MITRE authoring and deployment contracts

Conversion preserves every source tactic in order in
`properties.detectionAction.alertTemplate.tactics`, including two or more
entries. Multiple tactics alone are not an error or a `needsReview` reason.
Each entry contains only compatible source techniques/subtechniques. The
converter reuses the repository Sentinel validator's
`.script/tests/detectionTemplateSchemaValidation/Models/ModelValidationAttributes/KillChainTechniquesHelper.cs`
catalog and its base-technique matching semantics for subtechniques; this
catalog does not independently verify that a particular subtechnique suffix
exists. Source tactic identifiers are retained as target tactic strings, not
paired by position with the flat technique list. A technique shared by several
documented tactics can appear under each of those tactics, never under an
incompatible one. A tactic with no compatible techniques is retained without
inventing any. Unknown tactics, malformed IDs, unmatched techniques, or an
unavailable catalog remain blocking conversion/validation errors.
The Graph `mitreTactic.tactic` reference defines a string, not a public enum.

Original source lists remain independently preserved in
`contentProvenance.conversion.originalTactics` and `originalTechniques`.
Existing `ruleOverrides.<source-id>.tactic` plus `techniques` now correct only
the techniques of that named source tactic. They never narrow the list or
change source order; conversion emits an explicit legacy-override warning.
The tactic must already occur in the source, and techniques must be compatible.
An absent tactic, missing technique list, or invalid/incompatible override is
a blocking error, not a silently ignored decision. To change source tactic
intent, use the separate reviewed source-authoring process. Existing drafts
are refreshed only with the normal explicit overwrite approval.

**Authored YAML is not the deployed payload.** V3.1 ARM packaging copies only
the first tactic entry, including its compatible nested techniques, into the
deployment payload; it does not modify the multi-tactic YAML or provenance.
This is intentional classification loss, not validated classification or alert
parity. Direct Microsoft Graph deployment remains restricted to at most one
tactic because the verified service rejected multiple tactics with HTTP 400.
The direct deployment path fails instead of truncating or sending an illegal
multi-tactic payload. `deploymentReady` counts and per-result
`directGraphDeploymentReady` exclude authored multi-tactic documents even
when conversion and authoring structural validation pass. No runtime or
deployment success is inferred from authoring or packaging.

### Source-derived detection identity

Generated `properties.id` is `xdr-<full original Sentinel analytic rule
template GUID>`; `contentProvenance.source.id` retains the original GUID without
the XDR prefix. The prefix ensures a Graph-compatible leading letter, including
when the GUID begins with a digit. This is not a deployed Sentinel rule instance
ID, a name slug, or an eight-character prefix. Renaming a rule does not change
this ID; distinct full source GUIDs remain distinct. Source IDs must use the
hyphenated GUID format; their case is preserved.
Duplicate source GUIDs (including case variants) and existing output ID or
provenance conflicts block conversion rather than overwriting another rule.

After reviewing local edits, explicit `convert --overwrite` can migrate the
converter's old `xdr-<name>-<first-eight-source-ID-characters>` IDs **only for the
same source ID and source path with converter provenance**. The independent XDR
version is preserved and the detection remains disabled. An existing custom ID,
missing/conflicting provenance, or a relocated output requires explicit manual
reconciliation; `--overwrite` is not permission to replace unrelated content.
The legacy ID must be reproducible from the stored display name or current source
name; an unrecognized name-based ID also requires manual reconciliation.
Without `--overwrite`, changed output is a conflict. Source YAML is never edited.

An ID transition persists `contentProvenance.conversion.identityChange` and an
actionable warning in the YAML and conversion manifest/report; later conversions
retain that warning. This is a **local artifact change only**, not evidence of
cloud migration. No existing cloud rule is updated or deleted by conversion.
An optional read-only identity review may help diagnose known legacy IDs before
the separately approved deployment, which otherwise targets the new GUID
rather than the old name-based ID. Do not make a general pre-deployment
existence check a workflow gate; stop for manual reconciliation if an observed
ID has uncertain ownership or content.

Structural validation and packaging require the canonical `xdr-<GUID>` ID for
documents declaring Microsoft Sentinel / AnalyticsRule provenance or the
`sentinel-to-xdr-migration` converter. They do not impose this GUID identity
contract on unrelated Custom Detections. Packaging normalizes a bare originating
GUID to `xdr-<GUID>` on its packaging copy, leaves an already-prefixed ID
unchanged, and rejects unrelated custom IDs rather than silently replacing them.
The normalized identity is used consistently in installation, registration,
content IDs, catalog criteria, and their references. The authored YAML and
source provenance remain unchanged. Graph payload preparation applies the same
idempotent normalization. The existing ARM `[if(true(), '<ID>', '<ID>')]`
literal expression is unchanged.

### Entity mapping and schedule diagnostics

Conversion follows the documented [Graph entity mapping contracts](https://learn.microsoft.com/en-us/graph/api/resources/security-entitymappingconfiguration?view=graph-rest-beta)
and [Sentinel source identifiers](https://learn.microsoft.com/en-us/azure/sentinel/entities-reference).
In addition to Host, Account, IP, URL, AzureResource, CloudApplication, Mailbox,
and MailMessage, direct mappings include:

| Sentinel identifier | Graph collection and field |
| --- | --- |
| DNS.DomainName | `dns.domainNameColumn` |
| File.Name | `files.nameColumn` |
| MailCluster.Query / Source | `mailClusters.queryColumn` / `sourceColumn` |
| RegistryValue.Name | `registryValues.valueNameColumn` |
| SecurityGroup.DistinguishedName / SID / ObjectGuid | `securityGroups.distinguishedNameColumn` / `sidColumn` / `objectIdColumn` |
| FileHash.Value with query-proven constant Algorithm=SHA1 or SHA256 | `files.sha1Column` or `sha256Column` |

The hash proof accepts constant assignments in a simple single-table
`where`/`extend`/`project` pipeline, not an algorithm guessed from a column name.
Unknown/mixed algorithms, MD5, missing output columns, dropped fields, and
conflicting source identifiers remain warnings. Linked entities such as
DNS.DnsServerIp, RegistryValue.Key, File.FileHashes, and Process.ImageFile are
not scalar query-column mappings. No joins or synthetic fields are introduced.
Graph processes accept hashes, not Sentinel ProcessId/CommandLine; those source
fields remain unmapped. Graph's Amazon, Google Cloud, and OAuth collections do
not establish corresponding Sentinel source identifiers, so the converter does
not invent those mappings. These are converter limitations, not claims that
Defender lacks the entity type. The required Host/Account/Mailbox/IP asset gate
is unchanged.

When an unsupported source identifier has an available output value, conversion
uses the best supported target identifier available from the source mapping
and query projection, then retains the original query output column in
`customDetails` and records a hash-bound `reviewRequired` assumption. For
example, `Host.FullName` can provisionally map to the supported
`hosts.nameColumn` when no stronger supported Host identifier is available.
Supported host fields are defined by the Microsoft Graph
[`hostEntityMapping` contract](https://learn.microsoft.com/en-us/graph/api/resources/security-hostentitymapping?view=graph-rest-beta).
Existing supported host identifiers take precedence; unsupported target fields
and columns not emitted by the query are never invented. The review is not
auto-accepted and does not establish identity equivalence or parity.

### Supplemental entity evidence in custom details

Whenever source entity information lacks an equivalent final entity mapping,
the converter also binds the original output value under
`properties.detectionAction.alertTemplate.customDetails`. This applies to every
entity family, unsupported identifiers, ambiguous repairs, conflicting mappings,
and identifiers omitted by an explicit `ruleOverrides.<id>.entityMappings`.
For example, a supported `hosts.nameColumn: HostName` plus IP mapping can
retain the original Host.FullName value as
`customDetails.HostFullName: DeviceName`; if no supported host-name candidate
exists, an available Host.FullName output may itself be provisionally bound to
`hosts.nameColumn`. An unproven choice is explicitly marked for human review.
This best-effort assumption is nonblocking for conversion, structural
validation, and read-only runtime query/output-schema testing, allowing a
large batch to continue without per-rule pauses. It does **not** replace a
valid supported mapping, establish restored identity/correlation/semantic
equivalence, or claim alert parity. Statically missing output bindings,
conflicts, malformed content, custom-detail limits, other review reasons, and
technical/query failures retain their normal warnings, errors, and gates.
When destructive projections make an explicit output binding unprovable,
conversion retains that binding and emits a nonblocking warning that runtime
output-schema verification is required; this does not clear unrelated review
findings.
Pending entity review blocks packaging and deployment; only hash-current
human review can resolve it. Supplemental values never resolve independent
identity-confirmation reviews.

The [Graph `alertTemplate` contract](https://learn.microsoft.com/en-us/graph/api/resources/security-alerttemplate?view=graph-rest-beta)
defines each custom-detail value as a **query output column name**, not an event
literal or entity object. Its
[`alertCustomDetails` resource](https://learn.microsoft.com/en-us/graph/api/resources/security-alertcustomdetails?view=graph-rest-beta)
is an open key-value object. Source `customDetails` and per-rule override
`customDetails` are merged, with the same configured/catalog column renames as
converted KQL. Identical bindings are retained; a conflicting explicit key
blocks conversion without overwriting the source value. Malformed declarations
remain errors. Empty source objects remain empty when no supplement is needed.

Automatic keys concatenate the entity type and source identifier using
alphanumeric characters, for example `HostFullName` or `ProcessCommandLine`.
Existing keys are never overwritten. A collision uses `_2`, `_3`, and so on
in source mapping order; an existing detail for the same output column is reused
instead of duplicated. Repeated conversion is deterministic. Query-proven
equivalent mappings, such as an intact FullName decomposition into host name
and DNS domain, need no redundant supplemental key.
`contentProvenance.conversion.supplementalEntityDetails` records source entity
index/type/identifier, original and converted column, selected detail key, and
availability status. The actual detail bindings are normal Graph/ARM alert
properties; this provenance remains outside deployment properties.

Existing conservative KQL helpers distinguish known output columns, known
missing columns, unproven destructive projections, and runtime-binding-pending
output. Final projections that explicitly drop or rename a bound column remain
errors. For a non-final destructive projection whose effect cannot be proven
statically (for example, a `project-away` before an aggregate), an explicit
source binding is retained with a warning rather than treated as missing.
Automatic entity supplements are not invented from unproven output columns.
The converter never rewrites KQL to restore missing columns. Explicit source
bindings to statically missing columns are retained for correction but fail
validation. When output availability cannot be proven for other reasons, a
supplemental binding is labeled `runtime-binding-pending`, with an explicit
warning rather than an availability claim. Runtime plans include
`customDetailBindings`. Graph runtime validation
checks every binding against the returned schema. Imported successful runtime
results for detections with custom details must include the target query's
`schema` array (`name` or `Name` per column); a count alone is blocked, and a
missing bound column fails validation. Query execution alone does not establish
detail binding or entity correlation.

The [documented Defender limits](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules#add-custom-details)
are **20 key-value pairs per rule** and **4 KB combined custom-detail keys and
runtime values per alert**. More than 20 authored pairs or keys alone exceeding
4 KB is a blocking error; nothing is silently truncated. The public references
do not specify a separate per-key character limit, so none is invented.
Runtime event-value size cannot be established from column names or schema:
the converter warns that the service drops the whole custom-details array if
the runtime limit is exceeded. Schema success is not proof of value-size safety;
qualification must check actual values.

`contentProvenance.conversion.informational` and manifest result
`informational` explain preserved equivalents. A best-effort entity choice is
instead recorded in `reviewReasons` and as `reviewRequired`, even though the
draft can still have conversion `status: converted` so structural and
read-only runtime tests can proceed. Host.FullName is informational without
review only when a conservative query proof shows that retained HostName and
DnsDomain explicitly decompose that same value using the
`iff`/`substring`/`indexof` pattern. Merely having name/domain columns is not
proof. When proof is absent, retain the original value in custom details and
record the selected supported field as a pending assumption. Reassignments,
branches, conflicting values, missing output columns, other technical errors,
and independent review findings retain their own warnings/errors/gates; no
unsupported `fullNameColumn` is emitted.
The identity proof also permits `summarize` when the full name survives as a
bare grouping key; previously derived name/domain columns must likewise survive
unchanged if reused. Aggregate values and computed grouping keys do not prove
identity equivalence. Native-table schedule classification is independent of
that identity proof: comments and aggregation do not hide a known native
lookback, but aggregation still cannot establish equivalent time windows.

Schedule messages record source frequency/lookback and emitted target frequency
with a [public lookback reference](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules#lookback).
Native Defender fixed lookbacks are 4 hours for hourly rules, 12 hours for
3-hour rules, 48 hours for 12-hour rules, and 30 days for daily rules.
For a shorter Sentinel lookback than a documented native XDR service window,
conversion may add a `Timestamp >= ago(...)` event-time bound immediately after
the native table input and before any query filters, projections, or
aggregation. This is limited to a conservatively recognized single-native-table
pipeline with matching source/target input and established source event-time
semantics; a simple `TimeGenerated` reference is lexically rebound to
`Timestamp`. Original filters remain. Provenance records the original Sentinel
lookback, effective event-time window, fixed XDR service window, time-column
binding, transformation rationale, and late-ingestion risk. The HTML and
manifest distinguish a constrained event-time window from the larger fixed
service window; they do not claim identical service windows, cadence parity,
initial-run equivalence, or alert parity.

Joins, unions, historical/baseline branches, reassigned or ambiguous time
columns, unknown native inputs, and unproven source/target bindings are not
rewritten and remain `needsReview` with a specific reason. NRT and frequency
mismatches are not narrowed. A duration in a comment or string is not a time
filter; existing filters are never discarded. Sentinel-only/custom, mixed,
unknown, and longer-source-lookback cases retain their schedule diagnostics.
Late-arriving events whose event timestamp falls outside the inserted bound can
be missed, so generated transforms still require normal runtime validation and
qualification; conversion does not promote a rule to runtime-validated.

## Runtime query validation

When this or another conversion changes the persisted Advanced Hunting query,
the converter blocks previously passed validation and downstream workflow
stages while retaining the old reports as historical. Runtime results bind to
the exact KQL SHA-256: Graph results record `querySha256` for the executed XDR
query; imported Sentinel MCP/Log Analytics results must supply the same field
for the exact source query. Missing or mismatched hashes are blocked. A passed
validation stage requires complete current-hash Sentinel and Advanced Hunting
query families; only Authoring may explicitly pass as
`runtimeStatus=environment-blocked`, which is not a runtime-qualified result.
Failed KQL/runtime results cannot be relabeled as provider gaps, and provider
fallback must rerun the complete family. Zero rows establish execution only.
Hash-scoped review decisions also expire when either source or converted-query
hash changes.

The built-in source-runtime missing-schema whitelist applies across all
solutions, source queries, and runs. It contains exactly `IdentityInfo`,
matched case-insensitively and reported canonically as `IdentityInfo`. It
classifies only a current Sentinel/Log Analytics result that is a failed
HTTP 400 query with `SEM0100` explicitly identifying that table as unresolved.
The Azure Monitor SDK's preserved nested error structure and the message
`'summarize' operator: Failed to resolve table or column expression named
'IdentityInfo'` are supported, as is the equivalent explicit
`Failed to resolve table 'IdentityInfo'` diagnostic represented by provider
evidence. A missing column, another table, mixed/multiple errors, partial
provider/family failure, authentication/authorization/tenant/transport/timeout
failure, stale query hash, or changed inventory is not whitelisted.

No manual acceptance, actor, reason, run/rule authorization, or separate
decision artifact is required. The runtime derives the classification from
the exact current source query hash and complete family. It never rewrites or
relabels the raw provider result: that query remains `failed`. Reports preserve
the raw error alongside the canonical whitelist table and reason, and use
`source-waived` (never passed/success/executed) for the source disposition.
The status remains visible when Validation is blocked by XDR or other gates.

The whitelist does not relax any XDR runtime, exact-query hash, actual output
schema, `customDetails` binding, mapping-review, technical-validation,
packaging, deployment, ingestion, or parity gate. Validation may complete as
`runtimeStatus=source-waived` only when every other current source query,
every current XDR query and required schema check, and every unrelated
technical/review gate passes. Direct workflow-stage completion independently
enforces this. Any other failed, blocked, stale, incomplete, or not-run check
keeps Validation blocked. The Defender `IdentityInfo` documentation does not
prove availability in a selected Sentinel source workspace.

## Content-creator authoring policy and pending implementation

This section records the approved authoring policy and its implementation gaps.
It does **not** introduce a validation mode, waive an existing gate, or assert
that a schema resolver is implemented. The canonical
[workflow](agent-workflows/end-to-end-migration.md#validation) still governs
stage completion. The finite global `IdentityInfo` source-runtime whitelist is
documented separately under [Runtime query validation](#runtime-query-validation);
it does not create an optional-validation mode or waive unrelated gates.

### Schema responsibility and evidence

For authoring, assume that tables referenced by the source Sentinel rule are
expected to be available in XDR. Do not ask the content creator whether the
target resolves both tables or directory fields. This is an authoring premise,
not a guarantee about any deployment environment, onboarding, licensing,
permissions, data freshness, or populated columns.

The tool is responsible for resolving standard Defender and Sentinel schemas
through an **actually advertised official schema MCP/API capability**, when
authorized and available, or authoritative Microsoft documentation. It must
identify the source and target query surfaces and resolve columns in their
table/alias scope; it must not ask customers to supply `Timestamp` versus
`TimeGenerated` or the casing of `AccountUPN`. Public documentation can support
schema review without accessing a tenant; it does not prove runtime execution.
Never invent an MCP capability or initiate authentication/runtime queries after
the user has declined live validation.

For `_CL` tables, infer only from available, actual connector definitions, DCR
stream/output transforms, or table definitions. The suffix alone proves neither
columns nor types. Cite the evidence and distinguish **inferred from definitions**
from **verified against the applicable schema** and **runtime validated**.
Missing or conflicting metadata is a specific tool/evidence limitation, not a
reason to fabricate fields or ask the customer to guess. Resolve conflicts
before claiming a safe transformation.

### Repair metadata at both ends

Metadata inconsistencies are not resolved merely by copying them faithfully and
reporting an error. Within the approved content-authoring scope, the orchestrator
must repair unambiguous, schema-defined metadata errors in both the Sentinel
source and the corresponding XDR draft, then inform the user. This applies to
all metadata, not only connector dependencies. It is a source-authoring
maintenance step, **not** permission for the converter to edit Analytic Rules:
normal conversion remains read-only with respect to source content, and no
automatic repair engine is implemented by this policy.

Only mechanical corrections with one defensible interpretation may be made
without a further content decision. For example, when an AWSS3 entry contains
`datatypes: [AWSVPCFlow]` but lacks the schema-required `dataTypes`, rename that
key to `dataTypes` in the source, then explicitly refresh the corresponding
draft. Do not normalize valid connector IDs, data-type values, arbitrary
extension fields, order, duplicates, or absent/empty declarations. Conflicting
keys or values, ambiguous intent, tactic/technique choices, entity meaning,
identities, and release versions require an explicit decision; never invent a
resolution or copy platform-specific metadata across incompatible contracts.

1. Record the affected files, field paths, exact before/after values and schema
   basis. Preserve earlier reports and query hashes before replacing evidence.
2. Make the minimal approved source correction. Regenerate only the affected
   draft with the reviewed configuration and explicit overwrite approval; use
   `--rule-id` for an isolated repair so unrelated or deliberately deleted drafts
   remain untouched. Respect the [single-rule scope contract](#single-rule-conversion).
3. Check both declarations against their applicable schemas, their intended
   correspondence, unchanged KQL/identity/version/lifecycle, and unrelated-file
   hashes. Refresh conversion diagnostics through the existing tools, clearing
   only errors actually resolved; record the repair and checks in run evidence.
4. Tell the user what was repaired versus what remains unresolved, including
   affected files and before/after values. Reports must disclose their scope.
   Existing offline comparison pages and evidence exports remain historical
   snapshots unless explicitly refreshed; never pair old content with new hashes.
   Static metadata success does not make runtime checks passed: retain `notRun`,
   mixed-surface reviews, warnings, and all unmet workflow gates.

| Capability | Current implementation | Approved policy / pending work |
| --- | --- | --- |
| Standard schema resolution | `catalog.py` contains a finite table/rename catalog; `convert_query` applies token replacements. No general authoritative source/target schema resolver is implemented. | Resolve documented schemas and table-scoped lineage automatically; retain surface, source, and confidence evidence. |
| Mixed-query time columns | Native-only catalog queries may rename `TimeGenerated`; mixed native/passthrough queries preserve it and request review. | Resolve each reference against its actual table/alias, not a whole-query rename or a customer schema question. |
| Custom logs | `_CL` recognition identifies names, not a complete schema. | Infer only from actual available connector/DCR/table metadata; report missing/conflicting evidence explicitly. |
| Runtime validation declined | Offline Authoring can complete Validation only with current full-inventory conversion, structural success, resolved technical findings and hash-bound review decisions. It records `runtimeStatus=not-run` and is not runtime/XDR qualification. Existing runtime reports are never discarded or overridden. Qualification still requires its exact locked target and complete runtime/schema/consent evidence. | Show the disclosure below. Preserve unexecuted, blocked, failed, and review-pending results; a review acceptance is not runtime verification. |
| Entity equivalence | Documented identifier mappings and conservative proofs exist; unsupported mappings produce diagnostics. | Explain the exact retained identifiers, actual field loss, or proven equivalence; distinguish converter proof limits from target-contract limits. |
| Best-effort entity assumptions | Available unsupported entity values can use a deterministic supported candidate, remain in custom details, and carry hash-bound pending review while structural/read-only runtime tests continue. | Never auto-accept or claim parity; human review remains required before V3.1 packaging/deployment. Other technical and review gates remain unchanged. |
| General semantic uncertainty and batch review | Best-effort continuation is limited to specific entity-mapping cases. There is no general assumption-driven candidate workflow or batch accept/change/exclude interface. | For defensible uncertain mappings, generate a documented candidate and hash-bound assumption for later human review without per-rule pauses. Support scoped accept, change-and-regenerate, or reasoned exclusion while retaining every object and disposition in inventory/provenance. Acceptance does not prove runtime correctness or parity. |
| Non-representable rules and inventory coverage | Conversion diagnostics and full-inventory authoring cover current supported paths; there is no general diagnostic-candidate contract for a source object that cannot become valid deployable detection YAML. | Keep a complete denominator and explicit per-object outcomes. Emit non-deployable diagnostics outside XDR detection YAML rather than fabricate a runnable rule; unsupported, blocked, unprocessed, and excluded objects remain visible and are never silently dropped. |
| Source connector dependencies | Optional top-level `requiredDataConnectors` is deep-copied unchanged and structurally validated. Graph and inner ARM properties exclude it. | Repair schema-clear inconsistencies in source and draft through the authoring step above, then inform the user; converter source inputs remain read-only. Target-specific dependency translation/registration remains separate pending work; source declarations do not prove deployment readiness. |

When runtime validation is declined, the review UI should say:

> KQL has not been validated because this migration runs without runtime validation. Enable full validation, or review/accept the specific migration checks below.

This is approved presentation policy, not a claim that an “Enable full
validation” control exists. Offline Authoring's explicit
`validationMode=offline-authoring` route is permitted only after fresh full-inventory
conversion and structural validation, with all technical findings and
hash-bound review decisions resolved. It records runtime as not run, does not
dispatch Sentinel or Advanced Hunting queries, and cannot replace persisted
runtime reports. Current report failures and stale or unresolved evidence keep
the stage blocked. A provider report recorded after offline completion reopens
Validation and downstream gates for reevaluation. This is not runtime/XDR
qualification; Qualification retains its complete runtime, schema, consent,
target, and execution gates. Acceptance of a supported, specific migration
review item is not KQL execution, syntax verification, deployment readiness,
or alert parity. The separate Authoring `runtimeStatus=environment-blocked`
exception still requires its stated provider/environment evidence and may not
conceal an exact-query failure.

### Worked review: Local Admin Group Changes

The inspected source is
[`Analytic Rules/Persistence/LocalAdminGroupChanges.yaml`](../../Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/LocalAdminGroupChanges.yaml),
rule `63aa43c2-e88e-4102-aea5-0432851c541a`. Its parallel generated XDR YAML
was reviewed locally on 2026-10-07; it was not regenerated or executed.
Generated artifacts can retain older warnings and are not evidence that a
current converter proof has run.

The official references distinguish these contexts:

| Table / surface | Documented fields relevant here |
| --- | --- |
| [IdentityInfo — Sentinel / Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/identityinfo) | `AccountUPN`, `AccountSID`, `AccountCloudSID`, `TimeGenerated` |
| [IdentityInfo — Defender Advanced Hunting](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-identityinfo-table) | `AccountUpn`, `OnPremSid`, `CloudSid`, `Timestamp`; the unified schema also documents licensing/onboarding and UEBA-specific availability. |
| [DeviceEvents — Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/deviceevents) | `TimeGenerated`, `AccountSid` |
| [DeviceEvents — Advanced Hunting](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceevents-table) | `Timestamp`, `AccountSid` |

These are **documentation-verified schema facts**, not tenant verification.
`AccountUPN` to `AccountUpn` is supported for this IdentityInfo surface
transition, not a universal casing rule. In the inspected output that rename
occurred, but `AccountSID` and `AccountCloudSID` remain in the IdentityInfo
branch, while both event projections retain `TimeGenerated` from DeviceEvents.
Those retained references do not match the documented target schemas; they are
specific unresolved migration checks. IdentityInfo's source `AccountSID` and
target `OnPremSid` describe the on-premises SID; `AccountCloudSID` and `CloudSid`
describe the cloud SID. Resolving those references must respect the existing
`OnPremSid` alias, not blindly rename every occurrence. DeviceEvents'
`AccountSid` already uses the documented spelling on both surfaces.

The `leftouter` SID join with `NewUsers` and `innerunique` SID join with
`ADAZUsers` exist in both source and output. Any pre-existing filtering or
correlation limitations are source behavior, not a newly introduced migration
bug unless conversion changes their semantics.

[Sentinel identifiers](https://learn.microsoft.com/en-us/azure/sentinel/entities-reference)
are not interchangeable with the more restricted
[Graph host](https://learn.microsoft.com/en-us/graph/api/resources/security-hostentitymapping?view=graph-rest-beta)
and [Graph account](https://learn.microsoft.com/en-us/graph/api/resources/security-accountentitymapping?view=graph-rest-beta)
mapping contracts. Neither of these Graph mapping types documents a
`fullNameColumn`. For this rule:

- Host `HostName` and `DnsDomain` survive as `nameColumn` and
  `dnsDomainColumn`. The query explicitly splits the same `DeviceName` on its
  first dot, so the original host value is represented by that pair (including
  the no-dot case). The inspected artifact's Host.FullName warning must not be
  described as proven host-identity loss; the current conservative proof may
  still be unable to establish equivalence through this multi-branch query.
- Account `AccountName` and `laccountdomain` survive as `nameColumn` and
  `ntDomainColumn`, but they do **not** prove equivalence to `UserAdded` for all
  rows. When the NewUsers join has no match, `UserAdded` uses
  `DirectoryDomain\\DirectoryAccount`, while the mapped domain remains the
  unmatched `laccountdomain`. The directory-domain information carried by the
  source FullName mapping is not represented by the emitted account mapping
  on that branch. `UserAdded` remains in query output; it is mapping loss, not
  deletion of the query column. The retained SID joins themselves are unchanged.

### Connector dependency preservation and deployment boundary

For the same rule, source lines 8–12 declare
`MicrosoftThreatProtection` with data types `IdentityInfo` and `DeviceEvents`.
The inspected older generated artifact omitted this list. The correction is
implemented in the current working tree; existing artifacts are **not**
automatically rewritten. The source remains authoritative when explicitly
reconverting with the existing overwrite and identity safeguards.

```yaml
requiredDataConnectors:
  - connectorId: MicrosoftThreatProtection
    dataTypes:
      - IdentityInfo
      - DeviceEvents
properties:
  # Only supported detection-rule properties belong here.
  status: disabled
```

This is a partial authoring example, not a complete deployable detection.
Presence is significant: a missing source property stays absent; an explicit
`[]` stays `[]`. Entries, connector IDs, data-type spelling, order, duplicates,
and additional per-entry metadata are deep-copied without normalization.
Each entry must be an object containing a string `connectorId` and an array of
strings `dataTypes`; additional properties remain extensible. Nulls, scalar
lists, missing required members, and incorrectly typed members are invalid,
not silently dropped. At initial discovery, conversion retains malformed
metadata for review, records field-specific errors and `needsReview`, and
structural validation rejects it. It is never counted as successfully converted.
This preservation is not the final authoring outcome: follow
[repair metadata at both ends](#repair-metadata-at-both-ends) to correct
schema-clear errors in source and draft, or obtain a decision for ambiguous
conflicts, then report the repaired and outstanding findings.

1. [`build_xdr_document`](solution_manager/migration/converter.py)
   validates source dependency metadata against the output field schema and
   deep-copies it into optional **top-level** `requiredDataConnectors`, parallel
   to the Sentinel authoring field. Source identity, provenance, independent
   XDR release version, and disabled lifecycle safeguards are unchanged.
   `conversion.requiredWorkloads = ["sentinel"]` remains separate and is not an
   equivalent connector/data-type declaration.
2. The [YAML schema](schema/xdr-detection.schema.json#L99) requires selected
   provenance members and now explicitly validates optional top-level
   `requiredDataConnectors`. This does not make it a deployment API field.
   Existing documents without the field remain backward compatible.
3. [`graph_detection_payload`](solution_manager/qualification/deployment.py#L184)
   copies only `document["properties"]` into the Graph request. The
   [Graph detectionRule contract](https://learn.microsoft.com/en-us/graph/api/resources/security-detectionrule?view=graph-rest-beta)
   does not document `requiredDataConnectors`; its absence from that payload is
   not evidence of a missing supported deployment field.
4. The packager
   [`customDetections.ps1`](../Create-Azure-Sentinel-Solution/common/customDetections.ps1#L451)
   similarly copies `properties` into the MicrosoftSecurity extension resource.
   Its registration path (lines 311–316) emits only
   `dependency.requiredWorkloads`. Neither path emits source connector metadata
   into a deployed detection. The authoring YAML is retained unchanged.
   In contrast, the Sentinel rule path in
   [`commonFunctions.ps1`](../Create-Azure-Sentinel-Solution/common/commonFunctions.ps1#L2675)
   explicitly retains `requiredDataConnectors`.
5. The official [Sentinel alert-rule-template API](https://learn.microsoft.com/en-us/rest/api/securityinsights/alert-rule-templates/get?view=rest-securityinsights-2025-06-01)
   documents `requiredDataConnectors` with `connectorId` and `dataTypes`.
   The official [contentTemplates ARM reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.securityinsights/contenttemplates)
   separately documents plural `dependencies` with `contentId`, `kind`,
   `criteria`, and `operator`, including DataConnector/DataType kinds. That is
   **not** the same contract as the packager's singular
   `dependency.requiredWorkloads`, and it does not justify copying Sentinel
   YAML fields into detection-rule properties. The attempted public
   [Microsoft.Security/detectionRules ARM reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.security/detectionrules)
   returned 404 during this review: an authoritative exact-version
   MicrosoftSecurity extension contract was not established. No claim of
   extension support or runtime rejection is made.

**Verdict:** the previously confirmed loss of source authoring dependency
metadata is corrected for subsequent conversions by the top-level field. No
unsupported Graph/ARM field was added, and existing detection YAML must be
explicitly refreshed before it contains the correction. This is not a schema
resolver, validation waiver, or deployment action.

The [connector metadata tests](tests/test_connector_metadata.py) cover present,
empty and absent declarations, extension fidelity, deep-copy isolation,
malformed input/structural rejection, explicit reconversion and independent
version preservation, and actual local packaging exclusion from both install
and registration wrappers. Graph payload tests verify exclusion and isolation.
Conversion report errors use the existing reporting path. Sanitized evidence
allowlists and report/UI contracts are unchanged; no raw connector extension
metadata is added to evidence exports.

A separate target dependency model remains a future design decision. Any content-registration propagation
must first be checked against the exact extension/registration API version and
translated to its documented contract, not copied blindly. Package generation
logic, source content, existing generated artifacts, runtime gates, and workflow
state are not changed by this correction.

## Safety model

Conversion is conservative. A file is still generated when manual work is
needed, but `contentProvenance.conversion.status` is set to `needsReview` and
validation fails until blocking issues are resolved. The tool never changes
files under `Analytic Rules` and does not modify `Package/mainTemplate.json`.

The `search` review check uses KQL tokens rather than a raw word match. Line
and block comments, quoted/verbatim/multiline strings, and ordinary column or
binding references named `search` do not request operator review. Executable
`search` at query/pipeline boundaries (including nested queries) still requires
review and retains the existing `needsReview` gate. This is a conservative
lexical check, not a syntax or semantic validator; runtime validation remains
required. Other KQL checks and explicit review-acceptance rules are unchanged.
Previously generated findings are not rewritten: review stale acceptances
before an explicitly requested reconversion.

Generated detections start with:

```yaml
properties:
  status: disabled
```

### Independent XDR release version

New detections start with `version: 3.1.0` even when the source Sentinel rule is
`1.x`. `contentProvenance.source.version` continues to record the actual source
version; neither that source file nor its release version is promoted.
The required XDR version is a `major.minor.patch` string in `[3.1.0, 4.0.0)`.
It is distinct from `schemaVersion: 1.0.0`, `properties.id`, the converter
version, and API/provider versions.

Regeneration preserves an existing valid XDR version (for example `3.1.1`)
when the output belongs to the same source rule, including with `--overwrite`.
An invalid existing version or different source identity is a conflict, not
permission to reset the release. Resolve it explicitly before reconverting.
Files from older converter runs without a top-level version fail structural
validation and V3.1 packaging with reconversion guidance. After reviewing any
manual edits, explicitly reconvert with `--overwrite` to initialize `3.1.0`,
or author the independent XDR version. Never rewrite source provenance.
Solution bumps do not bump detection versions; authors manage subsequent XDR
content releases independently.

### Local parser bindings

Conversion automatically renames local `let` bindings that match a solution parser's
`FunctionName` or `FunctionAlias`. The shared PowerShell packager applies the same
normalization before building both the CD installation and its registration, including
when it receives previously authored detection YAML.

Names use `__xdr_inline_<original>` with a numeric suffix when necessary. Microsoft's
KQL parser and semantic binder identify the declaration and its references, including
nested scopes. This is not a text replacement: columns, strings, comments, parameters
that shadow the binding, and native parser YAML remain unchanged. Repeated runs are
stable. Conversion reports each rename as a warning, not a review blocker.

The normalizer checks syntax, binding identity, and inferred column shapes after editing.
It fails explicitly when a safe rewrite cannot be verified, including wildcard-selected
bindings, `union withsource`, and implicit output-column name changes. Use explicit inputs
and column aliases in these cases. Missing tooling is a setup error, not permission to
skip normalization.

This offline check uses the parsers shipped in the solution, including nested `.yaml`
and `.yml` files. It does not discover unrelated functions installed in a target tenant,
inline missing parsers, or replace live schema/query validation.

Requires Node.js and the pinned KQL dependency. From the repository root:

```powershell
npm ci --prefix Tools\SentinelToXDRMigration\kql
npm test --prefix Tools\SentinelToXDRMigration\kql
```

## Install

```powershell
cd Tools\SentinelToXDRMigration
python -m pip install -e .
```

## First-run setup

Run the guided setup once:

```powershell
sentinel-xdr-migration setup
```

If tenant security policy blocks device-code authentication, use interactive
browser authentication:

```powershell
sentinel-xdr-migration setup --hunting-auth-method browser
```

Setup checks the local environment and launches authentication only when it is
needed:

- `az login` for original Sentinel query execution through Log Analytics;
- a one-time Microsoft Graph device-code sign-in for Advanced Hunting.

Authentication tokens are managed by Azure CLI and the operating system's
credential cache. The toolkit stores only an authentication record and
non-secret configuration under `~/.sentinel-xdr-migration`.

Inspect readiness at any time:

```powershell
sentinel-xdr-migration doctor
```

Persist an approved non-production workspace once for confirmation and reuse
across solution workflows:

```powershell
sentinel-xdr-migration configure-workspace `
  --tenant-id "<tenant-guid>" `
  --subscription-id "<subscription-guid>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --workspace-customer-id "<workspace-customer-id>"
```

`doctor` returns both configured identifiers. Qualification still asks the
user to confirm the workspace for each new workflow, but it does not require
the ID to be re-entered.

### Per-solution Qualification target configuration

For a solution-specific Qualification target, copy the shared placeholder-only
example and replace its two values with the approved lab tenant and full
Log Analytics workspace ARM ID:

```powershell
$targetConfig = "Solutions\<solution>\.env"
if (Test-Path $targetConfig) {
  throw "Review the existing target config instead of overwriting it."
}
Copy-Item Tools\SentinelToXDRMigration\.env.example $targetConfig
```

`Solutions/<solution>/.env` accepts only literal `KEY=value` lines for
`AZURE_TENANT_ID` and `SENTINEL_WORKSPACE_RESOURCE_ID`. It is local
configuration, not authentication: do not put credentials, tokens, passwords,
or shell expressions in it. The example contains no real tenant/workspace data;
never edit it with customer identifiers. The solution `.env` is Git-ignored
and excluded from package content and optional evidence exports. It is not
automatically populated from process environment variables or the shared
`~/.sentinel-xdr-migration/config.json`; there are no implicit global target
defaults. Resolution is deterministic: an existing locked run is authoritative;
otherwise explicit CLI tenant/workspace values must agree with `.env`, and
`.env` supplies missing tenant/workspace values. Any disagreement fails closed
instead of applying a silent precedence rule. The subscription is always derived
from the validated workspace ARM ID.

Inspect the literal target before opting into a new Qualification workflow:

```powershell
sentinel-xdr-migration doctor --solution "Solutions\<solution>"
```

Then explicitly select Qualification and confirm the displayed local target:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile qualification `
  --confirm-configured-target `
  --version-bump none
```

The workflow initializer validates the ARM ID, derives its subscription ID,
checks the current Azure CLI tenant and active subscription, and only then
performs an exact `az resource show --ids <workspace-arm-id>` read to obtain
the workspace customer ID. It does not list or search for workspaces. A scope
mismatch or inaccessible exact resource stops initialization with an
actionable error; authenticate separately with the approved identity and retry.
Alternatively, explicitly supply both `--tenant-id` and
`--workspace-resource-id` on `workflow-init`; the subscription is derived, and
the workspace customer ID may be supplied or resolved from the exact resource.
Conflicting CLI and `.env` tenant/workspace values fail rather than silently
choosing one.

Once a Qualification run is locked, its persisted target remains authoritative.
Changing `.env` cannot retarget that run; a conflicting edit blocks resumption
and requires the normal explicit target-diagnosis/repair contract. Authoring
does not read or require `.env`, a tenant, Azure authentication, or a workspace.

Conversion and structural validation always remain available in offline mode.
Missing runtime access is reported explicitly and never blocks YAML generation.
For unattended inspection without opening sign-in prompts:

```powershell
sentinel-xdr-migration setup --non-interactive
```

The CLI setup covers Azure CLI and direct Microsoft Graph authentication. The
official Triage MCP is configured and authenticated in the agent host, not by
this Python package. For first use, configure:

```text
https://sentinel.microsoft.com/mcp/triage
```

Sign in with a supported tenant member identity and complete the tenant's
required Defender/Sentinel onboarding, consent, and security-reader access.
Guest identities may not work. The agent should verify that
`RunAdvancedHuntingQuery` is available before selecting Triage as its runtime
provider.

## Command line

### Contributor authoring guide

Select **Authoring**, **Qualification**, or **Cancel** before initialization;
there is no default profile. Authoring is the normal offline-capable content
workflow. Qualification is an explicit optional lab workflow, not a requirement
for publishing. Follow the [canonical stages and gates](agent-workflows/end-to-end-migration.md).

Authoring reviews the discovered source and existing output, converts the
complete solution, resolves each `needsReview` item with scoped evidence and an
explicit content-owner decision, structurally validates source and generated
YAML, and then packages through the repository's V3.1 entry point. Generated
detection IDs use `xdr-<full source Sentinel template GUID>` and remain
disabled by default; see [source-derived detection identity](#source-derived-detection-identity).

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --version-bump none `
  --campaign-id "<owner-selected-campaign-id>"

sentinel-xdr-migration inspect --solution "Solutions\<solution>"
sentinel-xdr-migration convert --solution "Solutions\<solution>"
sentinel-xdr-migration validate --solution "Solutions\<solution>"
sentinel-xdr-migration workflow-status --solution "Solutions\<solution>"
sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --version-bump none
```

Initialize a persisted Authoring workflow before packaging so the V3.1 build is
charged to its durable campaign. The `--campaign-id` must remain the same when
linking a replacement run; changing the run ID does not reset campaign usage.
Use the one version-bump action explicitly selected at workflow initialization
for the first packaging command; do not apply a second, additional version
bump. V3.1 packaging is the current repository entry point for hybrid/XDR
content. The package command does not validate KQL, deploy content, enable
detections, or prove registration support or alert parity.

Structural `validate` is distinct from live query execution. When live
validation is explicitly authorized, prefer capabilities actually advertised
by the official Sentinel Triage MCP. If a provider-level failure prevents a
complete query family from running, rerun that **entire family** through its
approved fallback—Log Analytics for the Sentinel source family or Microsoft
Graph Advanced Hunting for the XDR family—and record the provider gap. Do not
mix providers within a family or use fallback to conceal a genuine KQL error.
Imported results must bind to the exact persisted query hashes. Zero returned
rows show only that a query executed; they do not demonstrate behavioral
coverage, alert parity, or that data is present.

Keep operational reports, provider responses, workspace IDs, and raw lab
evidence under the ignored solution `Logs/` run directory. Review outputs
before sharing. The separate `export-evidence` command is an explicit,
allowlisted optional public snapshot under `Evidence/<run-id>`; it omits raw
messages and tenant identifiers, cannot be used to resume, and is not included
in a Marketplace package. Do not commit `.env` or `Logs/`.

The deterministic CLI provides conversion, structural validation, query-plan
and result-recording contracts, packaging, and reports. Autonomous selection
and dispatch of advertised MCP tools, cross-provider research, and an
interactive accept/reject decision experience are not implemented by this
package itself; follow the agent capabilities actually available and never
claim these pending orchestration features ran when they did not.

For offline Authoring, pass Validation only when the persisted discovery and
full-solution conversion stages are current, every source rule and generated
detection is present, structural validation succeeds for the complete
inventory, and technical findings plus hash-bound review decisions are
resolved. The stage records `runtimeStatus=not-run` with
`validationMode=offline-authoring`; this is authoring-only and explicitly not
runtime/XDR qualification. The route dispatches no queries. Existing runtime
reports—including optional Advanced Hunting results—cannot be replaced by
offline evidence; preserve and resolve their findings through the normal
runtime gates. No consent means no optional Advanced Hunting dispatch.

For an existing Authoring run whose passed Conversion stage predates
`manifestSha256`, recover that exact run's evidence before completing
Validation; do not reconvert, edit workflow state by hand, or create a
replacement run just to repair the receipt:

```powershell
sentinel-xdr-migration workflow-recover-conversion-evidence `
  --solution "Solutions\<solution>" `
  --run-id "<existing-authoring-run-id>"
sentinel-xdr-migration workflow-complete-stage `
  --solution "Solutions\<solution>" `
  --run-id "<existing-authoring-run-id>" `
  --stage validation `
  --status passed `
  --artifact runtimeStatus=not-run `
  --artifact validationMode=offline-authoring
```

Recovery is permitted only for a missing digest with the exact current run
manifest reference. It rechecks the complete recursive source inventory,
conversion results, generated-target provenance and hash-bound review state,
and full-solution structural validation before persisting the digest and
inventory binding. Any existing digest mismatch, scoped/changed manifest,
inventory drift, missing target, technical finding, or unresolved review
blocks recovery. The command does not modify source or generated detections.
If Validation is not already running, start it after recovery and before the
completion command.

### Opt-in full-inventory YOLO authoring

For resumable local authoring with a frozen recursive source-rule denominator,
initialize a **new** run with the already-selected profile and `--yolo`.
Qualification still requires its existing locked target; YOLO does not select a
profile, discover a workspace, or authorize environment writes:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --version-bump none `
  --yolo `
  --campaign-id "<owner-selected-campaign-id>"

sentinel-xdr-migration workflow-yolo `
  --solution "Solutions\<solution>" `
  --run-id "<run-id-returned-by-workflow-init>"
sentinel-xdr-migration workflow-status `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump none
```

The contract freezes every recursive `Analytic Rules` source path, identity,
source hash, and query hash for that run. It reuses existing discovery,
full-solution conversion, and structural validation; it does not invoke runtime
providers. `workflow-yolo-refresh --solution ... --run-id ...` imports only
existing provider reports bound to current query hashes; it does not run
queries or overwrite changed source or generated content. A stale inventory,
source/query hash, or generated target is a conflict to resolve explicitly,
not an invitation to shrink the denominator or discard user edits.

Coverage reports `N` (all frozen unique source rules), `M` (structurally valid
converted targets with no unresolved rule errors), and `E` (rules with an
unresolved error or suppressed disposition, counted once per rule).
Unprocessed, blocked, and suppressed rules remain in the denominator. Shared
provider/environment failures are recorded separately from per-rule errors.
The run stops when
`100 * E > 50 * N`; once stopped, better later evidence does not resume it.
`100 * M >= 80 * N` is advisory only and does not authorize packaging, PR
creation, qualification, deployment, ingestion, or any other write. The normal
review, validation, explicit approval, and packaging gates remain in force.

For YOLO runs, `package-v3-1` requires the passed workflow validation stage and
complete inventory to clear all technical and explicit-review gates. It
persists requested/effective/consumed version-action state and hashes the
package inputs, report, and artifacts. Retry with `--version-bump none` only
after the original action was consumed and when current inputs match the
recorded post-build hash; changed inputs require an explicit new bump choice.
Retries execute V3.1 again and must produce fresh evidence. Stale reports or
artifacts, including historical V4 evidence, cannot pass the packaging stage.

YOLO cannot be enabled by resuming a legacy run. Use `--new-run` with an
explicit profile and `--yolo` to start a separate run. Always select the exact
run ID when reading or writing if there is more than one. The optional
`export-evidence --include-authoring-contract --run-id "<run-id>"` flag includes
the selected run's validated contract projection in the explicit local evidence
export; the default export remains unchanged.

#### Durable campaign budget

Every new YOLO run requires an explicit `--campaign-id`. Campaign budgets are
opt-in for ordinary authoring workflows: pass `--campaign-id` to
`workflow-init` to bind one; without it, ordinary workflow initialization and
packaging retain their unbudgeted behavior and create no campaign artifacts.
The frozen inventory, policy, linked run IDs, and hash-chained append-only
receipts are stored outside the files-only run directories under the solution's
ignored `Logs/sentinel-xdr-migration-campaigns/<campaign-id>/` directory.
Resumes retain that binding. An explicitly linked replacement run must use the
same campaign ID and exact solution/inventory; changing the run ID does not
reset usage. A different campaign ID is a separate explicitly initialized
campaign, never an automatic retry identity.
Changing source inventory under an existing campaign is rejected; starting
another campaign requires an explicit campaign ID and reviewed scope.

The initial ceilings are 120 active minutes per campaign, 3 evidence-backed
rule revisions and 10 active minutes per rule, 3 full-solution conversion
passes, 3 V3.1 builds, 500 actual provider HTTP attempts including retries, and
one ingestion submission per exact approved pair/fixture attempt. Observation
deadlines are recorded per approved test in its schedule-aware UTC timestamp.
Rule-level revisions, HTTP attempts, ingestion submissions, and observation
polls have receipt APIs for provider/adaptation code; they are **not currently
dispatched by this Python workflow** and are not represented as enforced
provider limits. Each retry must call the provider-attempt receipt separately.
The current workflow measures and charges dispatched YOLO conversion passes
and V3.1 builds, including failed/cancelled calls. Active elapsed time is
measured around YOLO discovery, conversion, structural validation, and V3.1
packager calls (plus explicit observation API calls); manual workflow/report
bookkeeping and provider/deployment/ingestion/cleanup calls are not integrated.
Already-running work is not forcibly terminated if it overruns a ceiling, so
the active-time ceiling blocks subsequent work but cannot preempt an in-flight
call. The status report labels this coverage; no AI-credit or monetary usage is
inferred.

Inspect current usage and extend a ceiling only with an explicit actor, reason,
and owner-scope audit reference:

```powershell
sentinel-xdr-migration workflow-budget `
  --solution "Solutions\<solution>" `
  --campaign-id "<campaign-id>"

sentinel-xdr-migration workflow-budget-extend `
  --solution "Solutions\<solution>" `
  --campaign-id "<campaign-id>" `
  --dimension conversionPasses `
  --new-limit 4 `
  --actor "<owner>" `
  --reason "<reason>" `
  --reference "<approval-or-audit-reference>"
```

Exhaustion blocks new work and stops that workflow run without altering the
frozen coverage denominator or converting unprocessed rules into errors. An
extension never clears a stopped run, technical conflict, or approval gate;
after review, an explicitly linked replacement run can continue from the same
campaign's remaining allowance. Pre-budget runs are marked usage-unknown and
cannot dispatch budgeted work until an owner-reviewed measured baseline is
provided with evidence via `workflow-budget-reconcile-legacy`; historical use
is never reconstructed from timestamps or artifacts. Interrupted operations
remain pending and block dispatch until reconciled with an authoritative outcome
and measured elapsed time using `workflow-budget-reconcile`. Reconciliation
does not replay an attempt; an unknown ingestion result remains consumed and
requires a fresh marker and exact-scope approval before a new submission.
For legacy reconciliation, `--baseline` must reference reviewed JSON with all
seven fields: `activeExecutionSeconds`, `conversionPasses`, `packageBuilds`,
`providerHttpAttempts`, `ingestionSubmissions`, `ruleRevisions`, and
`ruleActiveSeconds`. The last two are objects keyed by every source GUID in
the frozen inventory. Attempt counters must be whole numbers. The CLI records
the submitted baseline and audit reference as owner-provided evidence; it does
not infer the values.

The existing CLI owns the run state under its workflow lock, while the shared
campaign ledger uses its own atomic writer lock and fsynced replacement. The
operation-start receipt is durable before dispatch; failed and cancelled
attempts remain charged. Receipt/hash or lock failures fail closed. Direct
Python calls to packaging internals and provider adapters that do not use the
receipt API remain outside enforcement; no such integration is claimed.

### Single-rule conversion

For an explicitly reviewed pilot or isolated refresh, select exactly one source
analytic rule template GUID (not a deployed rule ID or filename):

```powershell
sentinel-xdr-migration convert --solution "<solution-path>" --run-id "<run-id>" --rule-id "<source-template-guid>" --config "<reviewed-config.json>" --overwrite
```

`--rule-id` accepts one full hyphenated GUID, matched case-insensitively while
preserving the source's spelling in generated identity. Repeated selectors,
malformed IDs, no match, duplicate matching source IDs, and a selected ID present
in `excludedRuleIds` fail before creating or changing outputs, reports, logs or
state. Reconcile a selected exclusion explicitly; selection never means deletion.
All source/output identities and provenance remain inventoried for collision
checks. Existing overwrite, independent version, review, connector-metadata and
source-provenance contracts still apply.

Only the selected rule's nested output path may be written. All unselected drafts
remain byte-for-byte unchanged, even with `--overwrite` and unselected config
exclusions. Without `--overwrite`, changed selected content remains a conflict.
Omitting `--rule-id` retains full-solution conversion, including its existing
explicit-overwrite deletion behavior for excluded outputs.

The selected run's `manifest.json` and transformation report are replaced, not
merged with earlier full-solution results. `scope.kind=rule`, `scope.ruleIds`,
`scope.sourceTotal` and `scope.selectedTotal` identify exactly what was attempted;
counts describe only that rule. Repeated pilots do not accumulate full coverage.
Structural `validate` still checks all existing detection files and exposes
`conversionScope`; valid files are not proof that all source rules were converted.
Previously passed conversion/downstream workflow stages become blocked, retaining
historical evidence; discovery and qualification target locks are unchanged.
Solution-stage success and the toolkit packaging entry point are blocked until
full-solution conversion and the normal validation/review gates are completed.
Conflicts/needsReview still return CLI exit code 1; invalid selection returns 2.
A successful scoped conversion is only local rule authoring, never full-solution
readiness, runtime validation or approval to deploy.

Scope evidence and guards are run-local, just like other workflow evidence;
content YAML remains shared across runs. Do not reuse another run's prior
validation/package evidence after changing shared content. The selector does not
introduce scoped packaging, deployment, runtime validation or a gate waiver.

### Solution-local reports and legacy resumption

All new reports, logs, workflow state, qualification target, migration
configuration, and captured runtime evidence belong in
`Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/`. All solution `Logs` folders
are Git-ignored. Do not force-add them: provider responses, error messages,
query/alert evidence, and lab identities may be sensitive. Optional curated
PR snapshots are described below. Tokens/authentication records and reusable
cross-solution onboarding configuration remain in the existing user credential
store; they are never copied into a solution. Shared synthetic sample catalogs
and reviewed mock fixtures retain their existing `Sample Data` locations.

Each run has a collision-safe UTC timestamp/UUID ID recorded in `run.json` and
workflow state. `workflow-init` resumes the sole existing run by default.
`workflow-init --new-run --workflow-profile authoring --solution "<solution>"`
explicitly starts an isolated workflow with a new ID. Runs do not copy another
run's configuration, reports, or stage results. Detection YAML and Package
content remain shared solution content; a new run does not snapshot those files.

Use `workflow-runs --solution "<solution>"` to list IDs. Every solution CLI
command accepts `--run-id "<id>"`. When multiple runs exist, omitting it fails
instead of choosing the newest run or stale evidence. A selected nonexistent ID
also fails, except when explicitly applying a migration preview. Python callers
can scope existing APIs with `artifacts.using_run(solution, run_id)`. Direct CLI
writers without a workflow create one run on first use and reuse it thereafter.

Status reads can fall back to prior flat solution Logs,
`Reports/<solution>/sentinel-xdr-migration/`,
the old `AZURE_SENTINEL_REPORTS_ROOT` location, and report files in
`XDR Detections`. Reads warn but never move state or initialize a new workflow.
Before the next write, review and explicitly apply the copy:

```powershell
sentinel-xdr-migration migrate-reports --solution "Solutions\<solution>"
sentinel-xdr-migration migrate-reports --solution "Solutions\<solution>" --run-id "<preview-run-id>" --apply
sentinel-xdr-migration workflow-status --solution "Solutions\<solution>" --run-id "<preview-run-id>"
```

The entire copy is preflighted for conflicts. Originals remain untouched;
`<run-id>/legacy-artifacts.json` records their hashes. The preview's `runId`
must be passed to apply to use that exact destination. The previous flat-Logs
ledger is honored: newer flat workflow state supersedes the archived root
Reports state only when the archived original still matches its recorded hash.
Unreceipted conflicts stop the copy. Migrated artifacts belong only to their
importing run, never to subsequent new workflows. Changed legacy copies or missing
migrated files block resumption rather than selecting stale evidence. Repeated
apply is idempotent. Reconcile conflicts manually; never discard or replace
blocked workflow state. Nonportable/credential-bearing migration configuration
requires explicit review rather than automatic KQL rewriting.

Persisted known filesystem references are solution-relative (including the
run ID for reports), with `/`
separators. The workflow packaging gate and summary report resolve these
against the selected solution; old absolute and repository-relative references
remain readable. Move/copy external evidence into the solution before relying
on portability. External machine paths and raw provider messages are not
arbitrarily rewritten; Logs are not a sanitized public export. Lab tenant,
subscription, and workspace IDs are retained to preserve qualification locks.
Known credential fields, bearer tokens, and signed URL values are redacted in
report serialization, but this is not a guarantee that raw provider payloads
are safe to publish. Source queries and detection YAML are never sanitized or
rewritten by reporting.

Content discovery excludes `Logs`, `Reports` and `Evidence` subtrees. Only detection YAML
belongs under `XDR Detections`; solution Data content arrays and Marketplace
ZIPs must not include runtime artifacts. The old report-root environment
variable is read-only compatibility input, not a new-output override.

### Optional PR evidence export

After a run is stable, explicitly export its public review snapshot:

```powershell
sentinel-xdr-migration export-evidence --solution "Solutions\<solution>" --run-id "<run-id>"
```

This local-only command needs no tenant, authentication or cloud-write approval.
It writes only `Evidence/<run-id>/evidence.json` and `summary.md`, relative to
the selected solution. These files may be reviewed and committed; raw `Logs`
remain ignored. Export is never automatic, does not rerun tests, does not
update reports/state/logs, and refuses any existing destination (including the
same run). Multiple runs require explicit selection; legacy flat reports must
first follow the normal report migration process. Evidence is never a runtime
input, resume source, solution Data content input or Marketplace ZIP input.

Schema `1.0.0` is a fixed allowlisted projection: all eight stage statuses and
attempt counts, profile/version-bump decisions, fixed conversion, structural,
three runtime-provider, V3.1 packaging, query-parity, alert-parity and solution
reports. Every result is retained, including failed, blocked, pending, not-run,
excluded and needs-review results; unfamiliar statuses become `unknown`.
Missing/invalid reports and unsupported fields are explicit. Historical baseline
decisions and command history have no supported contract and are marked
unsupported, not inferred from prose. The exporter records its real version,
Python version and normalized invocation, not invented historical commands.
Generated detection provenance supplies converter/content versions when available.

The summary header names the public solution folder (never its local parent
path), run, profile and recorded workflow status. Structured `solution` metadata
distinguishes the current version observed in `SolutionMetadata.json` and the
single `Data/Solution_*.json` from the requested version action. Missing,
invalid, conflicting or multiple-copy version inputs remain unknown. A requested
target version is not inferred from a bump: there is no supported persisted
target-version contract. In particular, current `3.0.18` plus requested `minor`
does not claim that `3.1.0` was packaged. The UTC `exportedAt`, exporter version
and Python version describe this export, not historical migration execution.
Identical inputs and the same export timestamp produce the same projection.
Older snapshots without export timestamps render them as unknown; filesystem
modification times and current run facts must not be substituted.
Explicitly authorized header-only enrichment of an older snapshot must preserve
all original results, hashes and exporter identity. Record a separate UTC
`headerUpdatedAt` and `headerRenderer`; if reading today's solution version, mark
`solution.versionObservation` as `header-update`, not `export`. The renderer
labels this new observation separately and keeps an unrecorded original export
time unknown. This does not enable overwrite/refresh in `export-evidence`.

Only a checked public solution title, enumerations, bounded counts, strict
version/timestamp strings, SHA-256 hashes and
checked solution-relative content references are exported. No raw messages,
errors, queries, alerts, records, URLs, provider responses, arbitrary stage
artifact values, IDs or unknown fields are copied. Unsafe references (including
symlinks, traversal, identifier/credential-like or unusual filenames) are withheld.
Hashes describe export-time bytes; source-query provenance mismatches are
explicit, but historical validation-to-content hash binding is unsupported.
Reported passes are **not independently verified or trusted attestations**.
Changing observed inputs during export aborts it; export only stable runs.

Review the snapshot before publishing: solution names and content filenames are public-facing
metadata, and no heuristic can recognize every secret embedded in an otherwise
ordinary name. Titles with URLs, paths, control/markup characters or recognized
identifier/credential patterns are withheld. Rename sensitive content through the normal authoring
process, never publish raw operational reports to compensate for omitted detail.
Unknown report filenames/contracts are not auto-discovered or copied.

### Resumable end-to-end workflow

The repository agent uses a gated workflow manifest. Before initialization,
the user must explicitly select `authoring` or `qualification`; the CLI has no
profile default. The `authoring` profile coordinates discovery, conversion,
validation, V3.1 packaging, and final reporting:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --version-bump patch

sentinel-xdr-migration workflow-status --solution "Solutions\<solution>"
sentinel-xdr-migration workflow-next --solution "Solutions\<solution>"
```

Every packaging stage runs through:

```powershell
sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --version-bump none
```

For separate solution and toolkit worktrees, add `--toolkit-root "<toolkit-worktree>"`.
The command still uses the gated workflow packaging route: it invokes that
toolkit's `V3/createSolutionV3_1.ps1` (V3.1), while reading source content and
writing package files and evidence under the selected solution. The toolkit
root must contain the complete required V3.1 helper and template set. Without
the option, the solution's repository remains the toolkit root. The command
writes `Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\packaging.v3_1.json`.
A packaging stage cannot pass without that current-run V3.1 evidence and all
generated package artifacts.

Old V4 reports remain historical evidence; do not relabel them as V3.1.
When current solution inputs change after a successful package, `workflow-status`
shows `packageFreshness: stale` and `workflow-next` reports that an explicit
release action is required. Select the action against the exact package-input
hash reported by status, then package with that same action:

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

The new action must be explicitly `patch`, `minor`, or `major`; status reads
never change workflow state. The old V3.1 report and package artifacts are
preserved under that run's `package-history` evidence before rebuilding. A
changed input hash invalidates a pending choice. If a build consumes the
selected version but fails, a retry may use `--version-bump none` only for the
matching post-build inputs. Existing technical and unresolved entity-review
gates remain mandatory.

For the first V3.1 package of an offline Authoring run initialized with
`--version-bump none`, use the same explicit release-plan command with the
current package-input hash from `workflow-status` and select the intended
`patch`, `minor`, or `major` action. The offline validation record must be
current and bound to the complete inventory before this action is eligible;
Qualification continues to require its runtime-bound validation and selection
evidence.

An explicit target version may be selected instead of a bump when the release
must move directly to a particular supported V3.1 version. Targets must be
canonical numeric `major.minor.patch` versions in the inclusive range
`>=3.2.0` and `<4.0.0` (for example, `3.999.999`); the target does not have to
be the next consecutive version. Select the exact target at initialization, or
bind it to the current package-input hash when planning a later release. Use
`--version-bump none` with `--target-version`; a non-`none` bump and target
cannot be combined:

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

For a later release after inputs change, use
`workflow-plan-package-release --target-version <version>` with the current
input hash, then package with the same target. The V3.1 backend writes the
approved target to solution data and metadata. If packaging fails after that
version write, retry with `--version-bump none` and no target only when the
post-write input identity still matches; this rebuild does not change the
version again. Existing hash, approval, campaign, and packaging gates still
apply. This target route does not change independently authored Custom
Detection versions or the ReleaseNotes-only refresh workflow.

For an offline Authoring run whose package is already at the approved version
but whose release-note row was omitted, use the same-release refresh route
instead of choosing another patch/minor/major bump. It requires a current
successful V3.1 receipt, current full offline validation, and a clean package
input hash. The plan records the exact approved date and change-history text,
hashes every current package input, archives the old package evidence, and
expects only `ReleaseNotes.md` to change. Add the exact planned row immediately
below the ReleaseNotes table separator, then rebuild with `--version-bump none`.
Header labels and order are checked as trimmed Markdown table cells; existing
column-alignment whitespace and release-history bytes are preserved:

```

For a later, explicitly approved **non-ReleaseNotes** content correction that
must keep the already packaged solution version, use
`workflow-plan-same-version-content-rebuild`. This separate Authoring-only route
requires the exact current full package-input hash, the unchanged current
solution version, a successful V3.1 receipt from the selected run, and passed
current full-inventory offline conversion/review/structural gates. List each
approved changed input with `--changed-input`; ReleaseNotes paths are rejected.
The plan archives the old V3.1 receipt/artifacts and a hash-verified snapshot of
the current package inputs. The actual V3.1 build must use `--version-bump none`
without `--target-version`; it cannot change the solution version or substitute
for Qualification runtime gates. Every retry still runs V3.1 and must match the
same plan and inputs.

New V3.1 receipts include a complete per-file hash manifest for the successful
post-build package inputs. The planner derives the actual additions, removals,
and modifications by comparing that receipt-bound baseline with the current
input tree; the `--changed-input` set must match exactly. Unchanged declarations,
unlisted edits, and any ReleaseNotes change are rejected. For an older successful
receipt without a per-file manifest, planning fails closed unless
`--legacy-baseline-evidence` identifies a comparison JSON that reconstructs the
complete prior manifest and whose canonical aggregate SHA-256 exactly matches
the successful receipt. The evidence binds the prior receipt identity, current
input identity, file counts, and each changed path's before/current hashes.
New plans persist the evidence path and digest and recheck it on dispatch,
receipt acceptance, and retries. A pre-existing legacy plan without this binding
must pass the same `--legacy-baseline-evidence` path to each `package-v3-1`
attempt; no workflow state or historical receipt is rewritten.
If no exact baseline can be reconstructed, use the ordinary explicit
new-release workflow rather than weakening the same-version gate.

When a consumed V3.1 version action failed before a successful receipt was
written, the planner also supports an explicitly identified failed candidate.
Pass `--failed-candidate-evidence` with the selected run's persisted failure
handoff and `--legacy-baseline-evidence` with a comparison that reconstructs
the complete pre-repair input manifest against the failed attempt's recorded
input hash and file count. The planner verifies the failed attempt against
workflow state, validates and archives its generated candidate artifact
hashes, and stores the exact baseline manifest. It does not create or treat a
failed attempt as a successful receipt. If the baseline cannot be reconstructed
exactly, stop rather than infer missing file hashes or changed paths.

```powershell
sentinel-xdr-migration workflow-plan-same-version-content-rebuild `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --target-version 3.2.1 `
  --expected-package-input-sha256 "<current-package-input-sha256>" `
  --changed-input "XDR Detections\<rule>.yaml"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump none
```

For a failed V3.1 candidate with no successful receipt, add both evidence
arguments to the same planner command. The failure handoff must be under the
selected run's `Logs\sentinel-xdr-migration\<run-id>` directory. The comparison
must bind the failed attempt's exact input identity and file count and list
every changed, added, or removed package input; ReleaseNotes changes are not
permitted:

```powershell
sentinel-xdr-migration workflow-plan-same-version-content-rebuild `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --target-version 3.2.1 `
  --expected-package-input-sha256 "<current-package-input-sha256>" `
  --changed-input "XDR Detections\<rule>.yaml" `
  --failed-candidate-evidence "Logs\sentinel-xdr-migration\<run-id>\packaging-arm-ttk-failure-handoff.json" `
  --legacy-baseline-evidence "Logs\sentinel-xdr-migration\<run-id>\failed-candidate-current-input-comparison.json"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump none
```

For a legacy successful receipt, add the same solution-relative evidence path
to the plan command and, for a pre-existing plan, to every package attempt:

```powershell
sentinel-xdr-migration workflow-plan-same-version-content-rebuild `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --target-version 3.2.1 `
  --expected-package-input-sha256 "<current-package-input-sha256>" `
  --changed-input "XDR Detections\<rule>.yaml" `
  --legacy-baseline-evidence "Logs\sentinel-xdr-migration\<run-id>\same-version-content-rebuild\receipt-current-input-comparison.json"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump none `
  --legacy-baseline-evidence "Logs\sentinel-xdr-migration\<run-id>\same-version-content-rebuild\receipt-current-input-comparison.json"

sentinel-xdr-migration workflow-verify-same-version-content-rebuild `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --legacy-baseline-evidence "Logs\sentinel-xdr-migration\<run-id>\same-version-content-rebuild\receipt-current-input-comparison.json"
```

The verification command is read-only and proves package scope/receipt
integrity only; it does not mark the workflow complete or replace local suite
validation.

```powershell
sentinel-xdr-migration workflow-plan-release-notes-refresh `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --release-date "12-10-2026" `
  --change-history "Approved release-note text" `
  --expected-package-input-sha256 "<current-package-input-sha256>"

sentinel-xdr-migration package-v3-1 `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --version-bump none
```

The packaging gate verifies the exact approved row hash and rejects any other
input, inventory, or ReleaseNotes change. V3.1 runs again and must produce a
new receipt for the updated inputs; the old package is historical evidence,
not relabeled. The package version and consumed patch action are not changed
or consumed again. This route is Authoring-only; it does not satisfy or bypass
Qualification runtime, target, consent, or deployment gates. If the previous
package receipt is missing, stale, or no longer matches the complete current
input tree, use the ordinary explicit new-release workflow rather than this
same-version route.

For item-level failures in a complete run, use
`package-selection-plan --solution ... --run-id ...` to inspect every current
Analytic Rule and Custom Detection, including query and full-file hashes,
provider/target bindings, evidence paths, and exclusion reasons. Apply only the
reviewed plan with `package-selection-apply` and its exact
`--expected-plan-sha256`; this changes only the content-selection arrays in
`Data/Solution_*.json`, adding `XDR Detections` only when it was
absent and the plan bootstrapped candidates from the complete conversion
manifest. An explicit empty array stays empty; all current conversion outputs
remain represented as included or excluded inventory. The plan and receipt
are revalidated before the V3.1 build, and the generated template and ZIP must
match its selected and excluded inventory. Apply rechecks the staged file
identity and performs a post-receipt freshness check. The migration writer
lock serializes this tool's
own updates, and atomic path exchange detects changes present at the commit
boundary. Apply requires that no external editor or process modify
`Data/Solution_*.json` until it completes; external writers do not honor the
migration lock, so this is a caller precondition rather than a general
filesystem compare-and-swap guarantee. If a change is detected, apply stops
and retains conflict evidence where possible. A receipt published before a
later detected edit is retained but rejected as current selection evidence.
### Partial solution publication and Qualification

An evidence-based partial V3.1 package is allowed only when the number of
unique original Sentinel rule IDs represented by currently eligible,
deployable Custom Detections is **strictly greater than 50%** of the complete
current recursive source-rule inventory (`2 * validated > original`). Exactly
50%, under 50%, zero, and empty/invalid denominators are blocked. The
denominator is independent of `Data/Solution_*.json` selections; a missing
source from a manifest, scoped manifest replacement, duplicate reference, or
source-only Analytic Rule cannot reduce it or increase the numerator.

The selection plan records the original source inventory and hash, validated
migrated IDs, numerator/denominator, coverage, selected evidence scope, and
each excluded identity and reason. Only current structural, review, exact
source/target/provider/query, and required schema evidence counts. Malformed or
ambiguous global evidence remains fatal. The V3.1 package contains only
selected eligible items; excluded YAML and original failures remain visible
and unchanged. `partial-package-validated` is not full-inventory validation.

Qualification may continue for that same applied selection. Deployment,
ingestion, and alert-parity executors must use the exact selected AR/CD scope
and keep their existing per-item checks, target binding, permissions,
disabled-state, ownership, consent, immediate write approvals, and cleanup
gates. A successful selected-scope Qualification or parity result must never
be described as full-inventory success. A changed selection or bound artifact
invalidates the receipt/package and requires re-planning. Full conversion,
validation, packaging, and Qualification behavior is unchanged when the
complete inventory is valid. See the canonical
[evidence-based package selection contract](agent-workflows/end-to-end-migration.md#evidence-based-package-selection)
for exact limits and commands.

An explicit empty XDR array means no Custom Detection installation or
registration resources. A missing array can be bootstrapped only during
planning from manifest outputs; direct V3.1 packaging without an explicit
array still fails closed. Runtime reports must carry their own matching
run/provider/target execution bindings; sidecar authorization cannot make an
unbound report eligible. Current source structure accepts both Scheduled and
NRT kinds with their corresponding required/forbidden scheduling fields.

Package-version selection is unchanged, but V3.1 rejects effective solution
release versions outside `[3.2.0, 4.0.0)`, independent XDR Custom Detection
release versions outside `[3.1.0, 4.0.0)`,
and other content-item release versions `>= 4.0.0`. Explicit bumps that select
an out-of-range version fail without overwriting package files or persisting
the bumped source version. These are release bounds, not ARM API/schema bounds.
Older source solutions require an explicitly selected supported target or bump;
no-bump rebuilds below the solution floor are rejected rather than promoted.
XDR uses only its top-level YAML `version`, including when registration is
disabled. Registration metadata and content product IDs use that same version.
Data `XDR Detection Version`, solution version, and source provenance are not
fallbacks in V3.1. See "Independent XDR release version" above for older files.
`trackingId` in SolutionMetadata.json is the complete Partner Center
customer usage attribution ID, not a bare GUID, Partner ID, or plan ID.
When absent/blank, V3.1 attempts anonymous **public Marketplace catalog/template**
discovery (not authenticated Partner Center API access) using exact publisher and
offer identity and one unambiguous plan/marker. It saves the validated full ID
into authoritative SolutionMetadata.json and emits the current marker shape.
Explicit IDs win without lookup. Attribution is required when XDR detections
or Defender Workbooks are emitted: neither `-SkipAttributionLookup` nor
`SENTINEL_SKIP_ATTRIBUTION_LOOKUP=1` suppresses missing-ID lookup.
Lookup failure or ambiguity leaves metadata unchanged and terminates packaging
before package files/ZIP output. Verify publisher/offer identity and the
published plan/marker, or supply the correct full ID and rebuild.
For optional attribution only, the CLI inherits the environment control for
offline skips and preserves warning-only lookup failures in the packaging
report. Successful provenance is recorded separately in `attributionSources`.
Local metadata write failures stop packaging.
Partner Center cannot auto-add tracking for functional nested deployments.
If lookup cannot resolve it, obtain the ID from offer > plan > Technical
configuration, add it, and rebuild. Missing attribution does not imply upload
rejection. See the [V3.1 guide](../Create-Azure-Sentinel-Solution/V3/README-V3_1.md)
and [official attribution guidance](https://learn.microsoft.com/partner-center/marketplace-offers/azure-partner-customer-usage-attribution#microsoft-marketplace-azure-apps).

The workflow state is written to:

```text
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\workflow-state.json
```

Each stage is explicitly started and completed so interrupted runs can resume
without relying on conversation history:

```powershell
sentinel-xdr-migration workflow-start-stage `
  --solution "Solutions\<solution>" `
  --stage discovery

sentinel-xdr-migration workflow-complete-stage `
  --solution "Solutions\<solution>" `
  --stage discovery `
  --status passed `
  --artifact inspection="Logs\sentinel-xdr-migration\<run-id>\inspection.json" `
  --evidence "Analytic Rules\Example.yaml"
```

Stages accept `passed`, `failed`, or `blocked`. Failed and blocked stages
require an explanation and can be retried after their cause is corrected.
Downstream stages remain locked until every dependency passes. The contract is
defined by [`schema/workflow-state.schema.json`](schema/workflow-state.schema.json).

#### Event-driven durable coordinator

The optional local coordinator adds an accountable owner and a durable,
idempotent event/outbox registry around an already initialized workflow run.
It derives stage decisions only from `workflow-status` and `workflow-next`;
those existing commands remain authoritative for all stages, dependencies,
evidence, and gates. The ignored registry is local to the current checkout at
`Tools/ignored/sentinel-xdr-coordinator/registry.json`. It contains run and
target identifiers plus hashes, not credentials or provider response bodies.

```powershell
sentinel-xdr-migration coordinator-enroll `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --owner "<accountable-owner>"

sentinel-xdr-migration coordinator-reconcile `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"

sentinel-xdr-migration coordinator-status `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"
```

`coordinator-status` performs deterministic reconciliation and persists any
expired-claim, decision, and outbox updates; it is not a read-only registry
inspection.

An optional `--shared-dependency ACTION=KEY:PURPOSE` on enrollment records a
scoped external prerequisite. A hash-bound `shared-dependency-completed` event
re-evaluates only consumers of the same key, purpose, and target fingerprint.
For example, Graph `advancedHunting` evidence never satisfies
`customDetection` authorization. In Validation, source and Advanced Hunting
runtime tasks are reported independently; a blocker in one does not suppress
the other. These task views do not split or complete the canonical Validation
stage. Shared-dependency evidence is reported by its submitting actor and
hash-checked locally; the coordinator does not validate permission grants,
service configuration, or the truth of that evidence.

Claims are atomic, idempotent reservations for currently `ready` actions. They
do not start a stage or execute a CLI command. An executor must use the
existing stage and validation entry points, then submit a hash-bound completion
event; reconciliation consumes the handoff only when current official workflow
state or exact evidence supports it. An expired claim becomes blocked with an
unknown outcome. Cloud requests are never retried by the coordinator; an
accountable owner must resolve the outcome from authoritative evidence before
another attempt. An exact current target and evidence hash from the claim's
officially terminal workflow stage (`passed`, `failed`, or `blocked`) can
resolve it through the completion event or
`claim-resolved --outcome completed`; this records coordinator state only and
does not write or complete the official workflow stage. Confirming `not-started`
still requires separate hash-bound owner evidence.

When a terminal stage exposes a same-ID retry with changed evidence, the retry
remains blocked until the prior claim's completion handoff is validated against
its retained action snapshot and consumed.

Every changed decision, including `approval-needed`, is a durable outbox entry,
not an approval. Use `coordinator-event --kind approval-requested` to record a
separate exact action, purpose, and target request; a host adapter may read the
outbox and deliver it only after rechecking the current action hash and target.
Reconciliation supersedes stale outbox entries. `coordinator-ack` acknowledges
delivery only. No host messaging adapter, background daemon, authentication,
consent, deployment, ingestion, parity, or automatic command dispatch is
implemented. Qualification writes remain
blocked behind the existing exact-scope approval and guarded CLI paths.
Read-only preflight may be recommended but does not prove service settings,
permissions, or runtime results. Status/reconcile surface missing owners,
idle ready actions, running stages without tracked claims, expired claims,
unconsumed completion handoffs, and undelivered outbox items as watchdog
exceptions; the watchdog runs only when a CLI command is invoked.
An existing owner can record an auditable `owner-handoff` event to transfer
accountability; an ownerless work item can be re-enrolled with an explicit new
owner.

#### Solution watchdog best practice and `ACTION_REQUIRED`

Assign exactly one retained watchdog owner per solution/current workstream,
bound to its explicit run ID, profile, agreed goal, and approved scope. A
global observer may aggregate status but does not replace or duplicate the
owner. The existing owner performs the watch; do not launch replacement or
nested agents to re-check the same work. Missing ownership is escalated to the
responsible parent. Keep one read-only periodic watch until the goal is
verified complete or explicitly stopped/cancelled. Cadence is explicitly
configurable per coordination instruction; the current setting is three
minutes, not a fixed toolkit timer. Avoid hot polling and interruptions. A fresh run
retargets the same owner/schedule and preserves history without importing old
run successes. Completion requires the goal-specific persistent artifact and
bound evidence, not an idle agent, status message, toolkit commit, or
watchdog acknowledgement; stop the watch on real completion or explicit
stop/cancellation.

Use a prominent, stable `ACTION_REQUIRED` handoff through the existing agent
completion/handoff channel when an approved next operation has not started or
a concrete gate needs parent action. Include solution/run/goal/owner, exact
next operation or prerequisite, responsible parent, current approval
reference/scope (or `missing`), readiness evidence and stale/missing blockers,
last **real solution progress** time, elapsed stalled time (or `unknown`), and
a repeatable alert identity. Repeat it on each ordinary tick until genuine
progress, verified completion, explicit revocation, or an exact blocker
resolves it. Status updates, commits, and watchdog acknowledgements do not
reset the timer or clear the alert. The parent consumes the alert by performing
the already-approved bounded step, obtaining the required missing approval, or
reporting the precise blocker—not by waiting for the user to repeat the ask.

Example:

```text
ACTION_REQUIRED solution=ExampleSolution runId=run-example
goal=publish validated partial package (>50% migrated-CD coverage)
watchdogOwner=solution-owner nextOperation=apply reviewed plan and build V3.1
responsibleParent=parent-coordinator approval=granted/ref-01/local-authoring-only
readiness=blocked missing=2 of 3 source rules lack current validated CDs
lastRealProgressAt=2026-10-12T09:00:00Z elapsedStalled=28m
alertIdentity=ExampleSolution/run-example/selection-coverage
```

This is an orchestration best practice, not a new scheduler or CLI feature.
Read-only watchdog ticks do not authorize toolkit/content/workflow changes,
build/package operations, cloud/auth/ingestion/enablement/deletion, or other
writes. Actual operations remain with the existing sole executor and separate
approval gates. Do not repeat unchanged already-granted common choices or
expand beyond approved scope.

Deployment, mock ingestion, and strict AR/CD alert parity are optional internal
qualification stages. They are not required for ISV authoring, PR submission,
Partner Center publishing, or customer deployment. To include them in an
approved non-production lab workflow, initialize with:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile qualification `
  --tenant-id "<tenant-guid>" `
  --subscription-id "<subscription-guid>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --workspace-customer-id "<workspace-customer-guid>" `
  --version-bump patch
```

Qualification writes a locked
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json`. Live
commands load this context and reject any tenant, subscription, workspace ARM
ID, or workspace customer-ID mismatch.

Diagnose an unavailable exact ARM path without broad workspace discovery:

```powershell
sentinel-xdr-migration qualification-diagnose `
  --solution "Solutions\<solution>"
```

The diagnostic may perform one exact customer-ID lookup restricted to the
locked subscription. Apply its unique same-identity correction only after
explicit approval:

```powershell
sentinel-xdr-migration qualification-repair-target `
  --solution "Solutions\<solution>" `
  --approve-target-update
```

Inspect a solution:

```powershell
python -m sentinel_xdr_migration.cli inspect `
  --solution "Solutions\Azure Activity"
```

Convert every analytic rule:

```powershell
python -m sentinel_xdr_migration.cli convert `
  --solution "Solutions\Azure Activity"
```

Every conversion run automatically creates:

```text
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\transformation-report.html
```

The self-contained report shows attempted, converted, needs-review, and
conflict counts, followed by each rule's output status, warnings, and errors.
It can be opened locally without a server or external assets.

Validate the generated YAML:

```powershell
python -m sentinel_xdr_migration.cli validate `
  --solution "Solutions\Azure Activity"
```

Validate converted queries through Microsoft Graph Advanced Hunting:

```powershell
python -m sentinel_xdr_migration.cli validate-advanced-hunting `
  --solution "Solutions\Azure Activity"
```

The Graph runtime validator submits each current converted Advanced Hunting
query exactly as authored, once per detection (subject only to the bounded
provider retry policy). It does not run table, function, schema, or other
preflight queries. A query failure is reported against that exact query and
remains failed; provider and malformed-response failures remain provider
errors. Successful responses must include the provider-returned named and
typed output schema, including when the query returns zero rows. Reports retain
the actual schema, exact row count, and at most ten provider-returned sample
rows per detection. It creates:

```text
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\runtime-validation.graph.json
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\runtime-validation.graph.html
```

Agents using the official Triage MCP should inspect its advertised capabilities
and use suitable MCP tools first for all supported runtime query operations.
For Advanced Hunting, execute the queries from `validation-plan`, normalize the
results, and record them through the same reporting contract:

```powershell
sentinel-xdr-migration record-runtime-validation `
  --solution "Solutions\Azure Activity" `
  --provider triage-mcp `
  --results "<normalized-results.json>"
```

This creates `runtime-validation.triage-mcp.json` and
`runtime-validation.triage-mcp.html`. Each passed result must include
`querySha256`, the SHA-256 of the exact persisted Sentinel query submitted to
the MCP or fallback provider. Missing/stale hashes are recorded as blocked.
The public CLI does not implement or host an MCP server; the repository skill
invokes the configured official MCP.

The runtime report includes a derived `sourceWhitelist` assessment for an
eligible `IdentityInfo` missing-table result, bound to its exact
`querySha256`. The raw `results[]` entry remains failed and unchanged; the
assessment records the canonical table, reason, raw failure, and whether the
complete source family permits the source-only disposition. No manual
acceptance command or separate decision artifact exists. The consolidated
solution JSON/HTML and workflow dashboard also expose the classification
while keeping any XDR or unrelated validation blocker visible.

For a complete original Sentinel query family, the toolkit also provides a
native Azure Monitor Query SDK runner. It is an explicit Qualification-only
command: it requires the run's locked tenant, subscription, and workspace,
verifies the active Azure CLI tenant and subscription without signing in, then
uses `AzureCliCredential` pinned to the locked tenant and sends the locked
workspace customer ID to the query API. The credential deliberately does not
pass a subscription argument: Azure CLI rejects token requests that specify
both `--tenant` and `--subscription`; the active subscription is independently
checked before any query and is never changed. It does not use shell commands
to transport KQL, modify the query text, add a timespan, or discover
workspaces. Each request passes the exact source query string with
`timespan=None`. The default request timeout is 90 seconds, the complete
family budget is 30 minutes, and at most two bounded transient retries are
attempted per query. Authentication, authorization, transport, partial-result,
and KQL failures remain distinct; no KQL failure triggers provider fallback.

```powershell
sentinel-xdr-migration validate-sentinel-sdk `
  --solution "Solutions\<solution>" `
  --run-id "<qualification-run-id>"
```

This executes every recursively inventoried source Analytic Rule exactly once
per attempt and requires a one-to-one, current-provenance mapping to generated
detections; empty, scoped, stale, or incomplete families fail closed. Full
returned table schemas and rows—including typed values in deterministic JSON
form—are kept in the ignored run-local `runtime-validation.azure-monitor-sdk.json`
report. A successful zero-row response means only that the query ran; it is not
parity evidence. An optional `--provider-gap-evidence` binds this complete SDK
family to an approved Triage MCP provider failure. Query families are never
combined across providers. If any SDK query fails, is blocked, or is not run,
the current SDK attempt—including per-query diagnostics and family-completion
status—is persisted before the command returns failure. This replaces older
SDK evidence for the same provider and cannot qualify a fallback family as
successful.

Use the official Sentinel Triage MCP first when it advertises an appropriate
workspace-query tool. If it fails at the provider level, rerun the entire
family through the SDK command above or import externally executed results
under `--provider log-analytics-cli`; imported results still require exact
`querySha256` values. For Advanced Hunting, use the Graph runtime validator. A
genuine KQL error returned by Triage is preserved as a failed detection and is
not retried through another provider.

### Qualification deployment-scope planning and advance consent

For migration-related read operations, request one lab-wide approval covering
all selected solutions and reuse it while the lab definition is unchanged.
Display and record the exact lab identifiers, provider surfaces, and expected
read-operation families. Keep current run/query hashes and bounded execution
checks for every dispatch; adding a solution within that scope does not require
another approval. Reconfirm after a lab or primary-workspace change, approval
withdrawal, or read-scope expansion. This excludes interactive authentication,
Entra consent, roles, and environment writes, and does not bypass existing CLI
consent checks. See the canonical workflow's
[reusable lab read approval](agent-workflows/end-to-end-migration.md#reusable-lab-read-approval).

During initial Qualification preflight, ask the user to confirm that the
selected, locked Log Analytics workspace is configured as the primary
Microsoft Sentinel workspace in Microsoft Defender XDR for the identity used
for Advanced Hunting. Show its workspace name, customer-ID GUID, and ARM
resource ID, and record the confirmation with the selected run's preflight
evidence. An Azure CLI workspace selection or successful Graph authentication
does not establish this setting.

Microsoft Graph [`security/runHuntingQuery`](https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery?view=graph-rest-1.0)
uses the caller's primary workspace when `workspaceId` is omitted. Even an
explicit `workspaceId` can fall back to the primary workspace when the requested
workspace is unavailable or inaccessible. If the primary workspace does not
match the locked target, or the user cannot confirm it, keep default-workspace
Advanced Hunting execution blocked; do not silently query another workspace or
change the primary setting. User confirmation is preflight evidence, not
automated verification of the response's workspace, effective permissions,
query execution, or output schema. Reconfirm if the target, caller, or primary
workspace setting changes.

The deterministic runtime-query consent commands bind an explicit lab-read
approval to the confirmed primary setting and the two supported query
operation families. First attest the selected primary workspace and persist
the current run's local inventory:

```powershell
sentinel-xdr-migration confirm-primary-lab-setting `
  --solution "Solutions\<solution>" `
  --run-id "<qualification-run-id>" `
  --actor "<reviewer>" `
  --primary-setting-name "qualification-primary-workspace" `
  --confirm-primary-setting

sentinel-xdr-migration plan-runtime-query-consent `
  --solution "Solutions\<solution>" `
  --run-id "<qualification-run-id>" `
  --source-provider azure-monitor-sdk
```

Review the emitted plan before submitting an affirmative selection. It shows
the locked tenant, subscription, resource group, workspace ARM ID and customer
ID; solution/run/profile; exact rule/query inventory, counts and hashes;
provider routes; and authentication requirement classifications. Approve only
the exact Sentinel source-query family, Defender XDR Advanced Hunting family,
or both by repeating `--approve-family`; substitute the `planSha256` returned
by the current plan:

```powershell
sentinel-xdr-migration review-runtime-query-consent `
  --solution "Solutions\<solution>" `
  --run-id "<qualification-run-id>" `
  --expected-plan-sha256 "<planSha256>" `
  --actor "<reviewer>" `
  --approve-family sentinelSourceQueryFamily `
  --approve-family defenderXdrQueryFamily
```

No family selection is not consent. `--decline --reason "<reason>"` records a
non-authorizing decision; `--revise-plan` defers without granting. Use
`revoke-lab-runtime-query-consent` to withdraw an existing grant, or
`check-runtime-query-consent --family <family> --provider <provider>` to
inspect an exact current binding. The durable grant applies across solutions
and runs for the unchanged locked lab, primary setting, and selected read
families. Query hashes, counts, providers, and auth classifications remain
current per-run dispatch/evidence bindings; changes refresh the snapshot and
must pass runtime checks, but do not by themselves require another lab grant.
Interactive sign-in always needs a separate immediate prompt.

This read-family approval is distinct from both the broader preflight
resource/permission plan and deployment/write approval. It does not authorize
authentication, permission or role changes, or writes. Existing immediate
approvals for deployment, ingestion, packaging, parity, and cleanup remain
unchanged.

Authoring may optionally run read-only Defender XDR Advanced Hunting schema
checks against its own selected run. Initialize Authoring with an explicit
`--tenant-id`, select the exact run ID, review the current query plan, and
affirmatively approve only `defenderXdrQueryFamily`:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --tenant-id "<tenant-id>" `
  --version-bump none

sentinel-xdr-migration plan-runtime-query-consent `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"

sentinel-xdr-migration review-runtime-query-consent `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --expected-plan-sha256 "<planSha256>" `
  --actor "<reviewer>" `
  --approve-family defenderXdrQueryFamily

sentinel-xdr-migration validate-advanced-hunting `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"
```

This consent is bound to the exact run, explicit tenant, Graph auth binding,
and current Advanced Hunting query inventory; it is not reusable across runs
or solutions. The plan performs no provider call or workspace discovery.
Validation requires an existing cached Graph credential for that tenant and
retains the normal per-query execution and returned-schema checks. It does
not sign in, change permissions, select or retarget a workspace, run Sentinel
source SDK queries, or authorize packaging, deployment, ingestion, parity, or
other writes. Missing consent or cached authentication blocks dispatch. This
optional read path does not change Authoring's offline-first workflow.

During Qualification preflight, review the exact deployment/ingestion plan
before reaching any environment-write approval step. `preflight-deployment`
exposes the additive `deploymentPlanning` object. Its target comes only from
the selected run's locked `qualification-target.json`; this preflight does not
discover or switch targets, start authentication, or make deployment writes.
The existing solution-local `.env` is read only through the target
configuration resolver and is neither authentication nor consent. It is
excluded from source/package fingerprints and all package/evidence exports.

Persist a current local plan and review the exact scope:

```powershell
sentinel-xdr-migration plan-deployment `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"

sentinel-xdr-migration review-deployment-plan `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --expected-plan-sha256 "<planSha256-from-plan-deployment>" `
  --actor "<reviewer>" `
  --approve-component sentinelAlertRules `
  --approve-component xdrCustomDetections `
  --max-additional-custom-detections <reviewed-cap>
```

`plan-deployment` and `review-deployment-plan` make no cloud calls; the
approval command writes only the local `deployment-planning-consent.json`
artifact. Review the recursive source inventory, unique source-rule IDs,
current reviewed disabled drafts, eligible maximum additional Custom
Detections, exclusions, exact target/solution/version, current package/content
hashes, package resource types, and component-specific count caps. The eligible
maximum is an upper bound, not a guaranteed conversion count. Without a
current package or complete reviewed ingestion plan, those scopes are
provisional. `planSha256` binds the review to the complete current plan;
changed target/content/package identity, payload, resource family, package
flags, or cap requires re-planning and renewed consent.

At the initial consent request, preselect **Approve the broadest currently
bounded and available scope** as a proposal, not as approval. Show the exact
selected components and all caps, targets, resource families, and package
selection flag values, then require affirmative submission/confirmation.
Cancellation, closure, decline, or no response must not create an approval.
When both are fully available, the suggested scope may include the disabled
AR/CD pair and later `fullPackageAcceptance`; list every package flag by name
and value (for example, all five current flags as `true` only when the current
plan explicitly exposes those five valid selections). If ingestion,
conditional provisioning, table creation, parity, or cleanup is unknown,
provisional, unsupported, or otherwise not fully bounded, leave it out and
explain why. Suggest only the broadest valid subset; never widen unknown scope.

The direct route is disabled Sentinel alert rules plus Graph Custom Detections
as reviewed AR/CD pairs, with an explicit maximum-additional-CD cap. The
separate later `fullPackageAcceptance` component requires a current verified
V3.1 package and an explicit boolean choice for every package-declared
selection flag. It covers full-package installation and any selected XDR
installation/Content Hub registration—not package creation alone. Pair-first
deployment and later package acceptance are distinct routes. Stored playbook,
workbook, connector, API, and connection definitions are not approvals to
instantiate or enable those resources.

Optional components are `mockTelemetryIngestion`, `fallbackDcr`,
`fallbackDce`, and `customTableCreate`. Ingestion scope is not approvable until
the reviewed, run-bound plan identifies the destination and stream, payload
hash and record count, batch caps, bytes/cost/retention impact, contract,
transform and schema hashes, marker/timestamp fields, and one shared
payload-per-pair execution. Benign controls remain separate. DCR/DCE support
ingesting reviewed local mock data; neither is needed to generate mock data.
DCR and DCE provisioning are conditional, distinct scopes, and a DCE must be
explicitly selected or proven required. The current DCR resolver checks
registered exact resource-name candidates only; it does not discover
arbitrary solution-owned DCRs. A fresh exact check is required before
provisioning, and this limitation must not be described as proof of absence.

Custom-table creation is conditional only for an exact contract-proven absent
custom-log destination, and its plan includes the table resource, contract and
schema path/fingerprints, and column count. A present incompatible table is
blocked rather than altered. When a compatible native table such as
`CommonSecurityLog` exists, table creation is `not-needed`; do not create a
custom lookalike. Table creation, DCR/DCE provisioning, telemetry ingestion,
rule deployment, enablement, cleanup/deletion, retention changes, and role or
identity changes are separate operations and are not implied by another
component's consent.

Advance planning consent is distinct from permissions, technical readiness,
deployment evidence, and immediate exact-scope write approval. Missing,
false, unknown, stale, or declined consent never counts as approved; do not
infer it from “Continue,” token scope, environment identity, example counts,
or mock-generation hypotheses. Keep the existing explicit approval directly
before every environment write. A denied/missing plan consent must not block
independent read-only checks or offline Authoring.

For package acceptance, ARM validation/preview applies only where supported.
Bicep extensibility imports do not support `what-if`
([Microsoft Learn](https://learn.microsoft.com/en-us/graph/templates/limitations#unsupported-deployment-features));
do not pass or wait for a `what-if` result for that route. Ordinary ARM
previews do not prove extension acceptance, and ARM validation must not be
described as validating extension behavior. Approved deployment and readback
remain necessary.

### Post-validation ARM template deployment acceptance-only

This optional Qualification step submits the exact final V3.1 package
`mainTemplate.json` for every solution in the approved same-PR/lab batch. It
requires a fresh successful repository build-and-validate report for each
member and binds the report to the current package report, artifact hashes,
solution, and `ContentRoot`. The producer records whether the V3.1 packager's
source-input ordering was POSIX or Windows `Path` ordering, selected only
when that complete fingerprint matches the package report; consumers honor
the recorded semantics across hosts. `Package/` fingerprints keep their
separate ordinal ordering. Windows source ordering lowercases each path
component before ordinal component comparison, matching `PureWindowsPath`
rather than .NET `OrdinalIgnoreCase` string ordering. The earlier migration
validation stage is not a substitute.

Plan and review the exact batch before deployment:

```powershell
sentinel-xdr-migration plan-arm-template-acceptance-batch `
  --member "<solution-path>::<run-id>" `
  --validation-receipt "<build-and-validate-report.md>" `
  --shared-decisions "<shared-pr-lab-decisions.json>"

sentinel-xdr-migration deploy-arm-template-acceptance-batch `
  --member "<solution-path>::<run-id>" `
  --validation-receipt "<build-and-validate-report.md>" `
  --shared-decisions "<shared-pr-lab-decisions.json>" `
  --expected-batch-plan-sha256 "<batch-plan-sha256>" `
  --actor "<approver>" `
  --confirm-exact-scope-write "I approve the exact enumerated ARM template deployment acceptance batch"
```

Repeat `--member` and `--validation-receipt` in matching order for every
approved solution. The batch must exactly match the user-confirmed shared
workstream and locked lab. The command submits the reviewed template snapshot
through Azure CLI's resource-group ARM deployment route in Incremental mode,
with the locked workspace and every package-declared `Deploy*` selection flag
explicitly `true`; it never invents flags or changes the template. It does not
require an ARM `what-if`, resource-group resource read-back, or behavioral
tests for this specific acceptance result. A member succeeds only when the
recorded ARM deployment has terminal `provisioningState: Succeeded`. Failed,
nonterminal, missing, timed-out, or partial attempts remain failed/unknown in
durable evidence; never blindly retry an ambiguous write.

This receipt records ARM deployment acceptance only. It does not prove
MicrosoftSecurity import behavior, verified installation of each resource,
content read-back, alert activation, parity, or completed Qualification.
Incremental mode does not guarantee that deployment has no impact. Verified
installation and post-install activation are distinct gates.

### Qualification mock-ingestion DCR selection

The intended policy is to prefer a DCR explicitly listed or referenced by the
selected solution when it demonstrably supports the exact shared fixture in
the locked non-production workspace. Compatibility means the deployed DCR is
available at the intended destination, accepts the fixture's public input
stream and fields, applies the expected transform, writes the expected table
and schema, and is usable with the approved endpoint and permissions. For the
Logs Ingestion API, structured input uses a customer-authored `Custom-*` input
stream and `transformKql` to project/cast into a supported `Microsoft-*`
output stream; a public destination schema does not expose a connector's
internal parser or enrichment logic. The public
[`/v1/metadata` endpoint](https://api.loganalytics.io/v1/metadata) describes
schema, not ingestion capability or connector behavior; confirm the route
against the table feature matrix and never assume reserved or service-managed
columns are writable. See the
[Logs Ingestion API overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
and [table feature matrix](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables-features).
A packaged ARM-template reference alone does not prove that the DCR exists in
the target workspace. Do not confuse a DCR's internal ingestion identifier
with its public input-stream name, and do not enumerate other workspaces to
find a candidate.

If no solution-listed DCR meets that contract, a supported ingestion contract
may be used to author a separate, isolated DCR locally and provision it only
in the explicitly approved Qualification environment. A DCE is needed for
private-link ingestion or when the DCR has no ingestion endpoint; the current
contract tool may provision an isolated DCE as part of its supported route,
but DCE creation is not a universal Logs Ingestion API requirement.
“Locally” describes authoring the configuration, not a local ingestion
service. Never alter an existing connector DCR or add a stream to it to force
fixture compatibility. If the source table does not support the documented
ingestion path, use a documented native telemetry generator or block the
qualification step; never redirect the rule to a custom lookalike table.
Provisioning and ingestion each require the applicable permissions and
immediate, exact-scope approval. Ingestion acceptance alone is not visibility,
query matching, or parity evidence.

Before fixture preparation, run the read-only Qualification preflight and
report telemetry-write, DCR creation, conditional DCE creation, and
conditional destination-table creation permissions separately. Check DCE
creation only when the selected route actually includes a DCE. The preflight
is diagnostic-only and does not provision resources or grant write approval.
`unknown` or pending review is not a permission grant. A missing permission
blocks only the corresponding write; it must not suppress independent
read-only workspace, DCR, schema, or query checks. The command requires no
fixture. Pass `--run-id` when the solution has multiple runs; omit it only
when the run is unique.

```powershell
sentinel-xdr-migration preflight-deployment `
  --solution "Solutions\<solution>" `
  --auth-method azure-cli `
  --run-id "<run-id>"
```

It adds `dcrPermissionPreflight` to the top-level Graph report and writes
`qualification-dcr-preflight.json` under the selected run's
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\` directory. The
subreport records `status`, `workspaceQueryPermission`, and per-contract
`resourceReadAccess`, `tableSchemaCompatibility`, `ingestionAuthorization`,
`resourceProvisioningAuthorization`, and `tableCreationAuthorization`, along
with `reportPath`, `targetFingerprint`, `schemaFingerprint`,
`transformFingerprint`, `contractFingerprint`, `resourceFingerprint`,
`candidateProvenance`, and `candidateSelection`. `contractFingerprint` is the
SHA-256 of the registered serialized contract. `resourceFingerprint` hashes
the exact target workspace, candidate DCE/DCR/table IDs, returned resource
configuration/schema, and current resource states. Provenance is
`registered-contract-resolver`, and candidate selection is
`exact-contract-resource-names-only`.
`resourceProvisioningAuthorization` separately
reports `dcrWrite` and `dceWrite` at the exact resource-group scope; DCE write
is checked only when the selected missing-pair plan includes DCE provisioning.
Per-capability authorization statuses are `ready`, `denied`, `unknown`,
`not-yet-verifiable`, or `not-needed`; table schema status is `compatible`,
`blocked`, or `unknown`; workspace query permission is `ready`, `denied`,
`unknown`, or `not-checked`; aggregate report status is `ready`,
`action-required`, `blocked`, `unknown`, or `not-applicable`.
`resourceReadAccess` can be `ready`, `denied`, `unknown`, or `unavailable`
(including HTTP 401); `targetVerification` can be `blocked`, `unavailable`,
`confirmed`, or `not-checked`.
A `ready` permission means the effective permission pattern was inspected,
not that upload, table visibility, or query matching succeeded. Treat all
results as read-only diagnostics; they do not authorize provisioning or
ingestion. Unknown or pending-review permissions must not be reported as
granted.

**Implementation status:** The current registered-contract resolver checks
contract-specific resources in the locked target workspace; it does not yet
discover or prefer a DCR referenced by the solution. Treat solution-first
selection as the intended policy, not an implemented automatic resolver.
Until that integration exists, report the resolver's actual
`compatible-existing` or `provisioning-plan` result and do not claim that a
solution-listed DCR was selected unless its compatibility was explicitly
established.

## Strict live alert parity

Query execution alone does not prove migration parity. In a non-production lab,
the optional alert-parity workflow temporarily enables an already deployed
Sentinel Analytic Rule and its migrated Custom Detection, ingests a reviewed
payload containing a unique marker, and compares normalized alerts strictly.

For full internal qualification, create a JSON plan containing one contract,
payload, unique marker, and expected malicious key set per converted detection,
then enable all pairs and ingest all fixtures:

```powershell
sentinel-xdr-migration start-alert-parity-batch `
  --solution "Solutions\<solution>" `
  --plan "<qualification-plan.json>"
```

The plan must cover every converted detection. All rules must begin disabled
and are disabled again if any enablement or ingestion fails.

For targeted troubleshooting, start one or more explicitly selected rule
pairs with a shared fixture:

```powershell
sentinel-xdr-migration start-alert-parity `
  --solution "Solutions\<solution>" `
  --contract "<ingestion-contract>" `
  --payload "<mock-json>" `
  --scenario-marker "<unique-marker>" `
  --expected-match-key "<expected-malicious-key>" `
  --detection "<Detection.yaml>"
```

The command requires both rules to be disabled, enables them, invokes the
separate `azure-monitor-logs-ingestion` CLI, and emits provider-neutral capture
queries. It does not use fixed sleeps. Prefer official Sentinel Triage MCP
query tools and use the documented CLI/API fallbacks only for provider-level
failures.

After normalizing both alert sets, complete the comparison:

```powershell
sentinel-xdr-migration complete-alert-parity `
  --solution "Solutions\<solution>" `
  --results "<normalized-alert-results.json>"
```

Strict parity requires equal alert counts, stable match keys, severity, tactics,
entities, and decisive evidence. The observed keys must also equal the declared
malicious match-key set, so a benign false positive on both platforms still
fails. Completion disables every selected rule in a cleanup path even when
comparison fails. If capture cannot be completed, run:

```powershell
sentinel-xdr-migration abort-alert-parity --solution "Solutions\<solution>"
```

State and reports are written under
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>` as `alert-parity-state.json` and
`alert-parity-report.json`.

## Consolidated solution report

Build one solution-level JSON and HTML report after any stage:

```powershell
sentinel-xdr-migration solution-report `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>" `
  --ingestion-report "<stream-one-ingestion-report.json>" `
  --ingestion-report "<stream-two-ingestion-report.json>"
```

The report includes every source rule, AR and CD identifiers and statuses,
conversion and structural results, runtime providers, deployment, strict alert
parity, entity recommendations, ingestion artifacts, and complete structured
errors. The HTML renders detailed errors in expandable sections; the JSON
retains the complete sanitized provider response rather than only a summary.

### Adaptive migration-flow schematic

The offline HTML report places a keyboard-accessible subway schematic directly
below the title and snapshot timestamp. Its first informational station is
**Necessary setup / initial preflight**, before Discovery. That station displays
only persisted run/profile/target records and any already-recorded, scope-bound
authentication or planning-consent evidence. It does not run the doctor,
authenticate, inspect local auth caches, or make network calls. Missing local
tool checks and authentication remain unknown/not recorded; `.env` target
configuration is not proof of access or approval. The current report schematic
shows a read-only preflight before deployment as an informational station.
Treat its exact-rule existence/readability checks as optional diagnostics, not
a separate deployment gate. The optional mock-ingestion stage still requires
its DCR/permission preflight.

The added Setup stop is informational, not a canonical workflow stage or gate.
Authoring runs show it before the compact mandatory route
**Discovery → Conversion → Validation → Packaging → Report**; Validation
remains required and the optional lab branch is omitted. Qualification runs
show a display-only post-build sequence: a distinct official local validation
rerun, read-only preflight, disabled direct AR/CD testing pairs, reviewed-fixture
ingestion, semantic/query validation, alert parity, then separately approved
full-package deployment/read-back before Report. This illustrates the selected
pair-first test plan; it does not reorder or redefine canonical workflow stages.
Full-package acceptance is separate from the V3.1 package build, and neither
package files nor pair results prove full-package acceptance. The full-package
step is shown as not tracked/not run unless separate execution evidence exists.
Publication is optional and outside the tracked workflow.
Legacy reports without confirmed mode remain **Mode not recorded**; attempted
qualification-stage evidence is still shown rather than hidden.

Every station circle and label is a keyboard-accessible link to its evidence
section; missing evidence opens an explicit unavailable/not-recorded explanation.
Safe local artifact links are rendered only for existing files inside the
selected migration run. Selecting a station shows its recorded stage status,
remarks, evidence references, timestamps, and elapsed time when available.
The preflight panel separates the required
`CustomDetection.ReadWrite.All` grant from read access, exact GET results,
effective RBAC, and deployment readiness; a successful GET or read grant is not
a deployment-ready result. The diagram calls out
an overall blocked/failed workflow independently from individual passed stages;
a package is shown as passed only when the recorded package-freshness check is
current. External publication is always marked **Not tracked** by this workflow:
building a package is not evidence that it was published. This is a generated
snapshot, not live status, and station selection is informational only.

An upfront package-resource inventory is planning context, not an approved
deployment scope. It reads resource types from the generated ARM template,
including nested arrays and language-version 2 resource dictionaries, and
displays API versions and the current template hash when verifiable. Separate
DCR/DCE Qualification resources are not inferred from package content. Prior
planning agreement and exact-scope write approval are distinct; the latter is
still required immediately before each environment write. The report cannot
authorize or initiate deployment, ingestion, cleanup, or any other write.
When a persisted deployment-planning contract exists, the panel also shows its
selected profile/mode, target and package identity, plan/artifact fingerprints,
source inventory and scope caps, resource inventory, component plans, selected
flags, and hash-bound advance-consent scope. Missing, provisional, stale, or
unknown planning metadata remains explicitly unapproved; planning consent never
substitutes for immediate exact-scope write approval or readiness evidence.
Controlled alert-parity and owned-resource-cleanup coverage, when present, is
displayed as non-consentable planning metadata with its recorded bounds/status;
it never represents advance consent or write authorization.
The subway precedes this technical planning panel. Planning status and target
summary are concise; the full candidate package-resource inventory occupies
its own readable, horizontally scrollable table, while hashes, raw scope
identifiers, package defaults, and detailed component evidence are expandable.
The inventory table alone scrolls horizontally on narrow screens.

The offline HTML dashboard opens in **Needs attention**, with single-select
status chips, search by name/path/ID/finding, and multi-select issue categories.
Status, search, and category filters combine with AND; selected categories
combine with OR. Chip counts cover the full report. Shared-issue buttons reset
the other filters and show the affected rules. **Clear filters / show all**
restores the complete list.

Finding types are separate from readiness and have their own filter, affected-rule
counts, text/icon badges, shared-finding sections, and original-evidence sections:

- **Errors:** recorded hard errors or actual failed checks/executions.
- **Reviews:** explicit unresolved review reasons or recorded human-review flags.
- **Warnings:** nonblocking advisories, including source lookback/schedule warnings.
  These never become errors, human-review flags, or readiness failures merely
  because the UI displays them.
- **Blocked prerequisites:** recorded blocks, distinguished from execution failures.
- **Information:** explicit backend `informational` notes, such as a proven
  equivalent mapping or matched cadence/effective lookback. They are neutral,
  nonblocking context, never inferred by downgrading warning text. The selected
  manifest is authoritative (including an explicit empty list); only an absent
  field falls back to the draft's conversion provenance. JSON includes per-rule
  `informational`, total `summary.informational`, and `summary.rulesWithInformation`.
  Transformation HTML has a separate Information column; dashboard information
  has its own badge, filter, shared groups, and detail disclosure. Information alone
  never creates a review flag, failure, or Needs attention status.

Choosing a finding type resets the status filter to All, so the Warnings filter
also reveals advisories on ready rules. Search/categories still apply; status can
then be refined. Compact rows prioritize errors and reviews, with warnings in a
clearly labeled advisory disclosure. Counts deduplicate identical inherited
diagnostics per rule. A warning repeated verbatim as an explicit review reason
is counted once as a review, preserving both original records in its evidence;
unrelated warnings remain warnings. Types can overlap on the same rule.

The shared **Preserve source tactics; review historical single-tactic findings**
explanation labels older single-tactic findings as historical and recommends
explicit draft regeneration, not mandatory narrowing of authoring metadata.
Current verified Defender UI / Graph beta behavior (2026-10-07) uses one
tactic with multiple compatible techniques/subtechniques; the isolated beta
multi-tactic create request was rejected. The documentation's collection-shaped
`alertTemplate.tactics` property does not alone establish multi-tactic acceptance.
The explanation links the public Graph `alertTemplate` and `mitreTactic` references,
without including raw lab details or claiming ARM/future-version validation.

Affected rule details show the current Sentinel tactic and technique lists
independently, the original lists retained in conversion provenance, and the
exact current draft tactic/technique/subtechnique structure. Lists are never
paired by position. A first-original-tactic draft with no techniques is labeled
an unapproved fallback shape only when those recorded facts match. The report
provides a rule-ID-specific, placeholder-only `ruleOverrides` example for optional
technique corrections to one existing source tactic, without removing or
reordering other tactics. It never recommends a tactic from rule
names or silently applies an override, approves a mapping, edits KQL, or clears
review gates. Absent classification metadata remains explicitly unrecorded.

### Automated-check doughnut chart

The compact **High-level findings** pie appears near the top, separately from
the unique-rule doughnut. Its red slice counts distinct error findings, yellow
counts warnings plus review findings, and sky blue uses the theme link token for
informational findings. Findings are deduplicated within each rule using the
same evidence-preserving rules as the table; one rule can contribute multiple
findings. Blocked prerequisites are stated separately rather than counted as
errors or silently mixed into this pie.

A **green standalone rule metric**, not a slice, shows rules whose automated
conversion and structural checks passed with no actionable findings or per-rule
block; informational notes are allowed. It is not a deployment/semantic approval.
The pie legend and keyboard-accessible slices filter matching rules, so the
result-list count can differ from the slice's finding count. Selecting either
chart clears the other chart's selection; normal filters can then narrow it.

The self-contained SVG chart counts each rule exactly once, in this priority:
**red** actual errors; **yellow** warnings or explicit review decisions;
**green** converted plus passed local structural checks, with no warning/review
or per-rule prerequisite block (informational notes are allowed); **gray**
insufficient evidence or an otherwise unresolved per-rule prerequisite block.
Green is labeled **Automated checks passed**, not deployment approval. It is
independent of the run-level conversion review gate: a green rule may still have
the status **Readiness unconfirmed**. Historical semantic cautions stay at run
level, not fabricated per-rule flags. Legend buttons provide counts/percentages
and a text alternative; both segments and buttons support keyboard filtering.
Chart selection resets other filters, which can then narrow the chart group.
The existing status controls and rule badges remain available.

### Reviewed bulk tactic exports

The dashboard supports **pending review/export**, never automatic resolution.
Only historical explicit single-tactic review findings with unique source IDs, valid source
choices, and a recorded source-file SHA-256 are eligible. Select visible eligible
rules or individual rules, choose a source tactic to correct, then choose techniques
and confirm compatibility/observable behavior **individually for each rule**.
Incompatible source tactics are refused with a reason; applying a new bulk
tactic clears prior technique selections and confirmations. No compatibility
cross-product is invented. Rules needing a new tactic/technique absent from the
source lists, an empty technique selection, missing metadata, mapping redesign,
or timing/data-loss acceptance require individual review outside these controls.
There is no blanket `acceptedReviewReasons` export.
These legacy controls are optional technique corrections, not a requirement to
choose one tactic for authored YAML. Conversion retains all source tactics in
source order regardless of the selected override. Regeneration, rather than an
exported decision alone, refreshes historical conversion findings.

Import the existing **complete JSON configuration** to merge unrelated root
settings, rule overrides, and other fields within selected rule overrides.
Only selected `tactic` and `techniques` fields are replaced, with previous and
new choices shown in the preview. Alternatively, explicitly confirm there is no
existing configuration to preserve. JSON is valid YAML for the existing CLI.
For an existing YAML configuration, create a JSON equivalent locally first:

```powershell
python -c "import json,sys,yaml; print(json.dumps(yaml.safe_load(open(sys.argv[1], encoding='utf-8-sig')), indent=2))" existing-config.yaml > existing-config.json
```

The browser never writes to the repository or calls a server. It downloads:

- `migration-reviewed-overrides.json`: the complete merged CLI configuration.
- `migration-reviewed-overrides.review.json`: a separate audit manifest containing
  selected source IDs, source file hashes, report/run identity, explicit choices,
  individual confirmations and prior selections; `applied` remains `false`.

Inspect both previews and compare source hashes against the current checkout;
re-import if the underlying configuration changed. **The CLI does not enforce
the review manifest or automatically reject stale decisions.** After explicit
review, apply the merged configuration through the existing tool:

```powershell
sentinel-xdr-migration convert --solution "<solution-path>" --run-id "<run-id>" --config "<downloaded-merged-config.json>" --overwrite
sentinel-xdr-migration solution-report --solution "<solution-path>" --run-id "<run-id>"
```

Do not pass the review manifest as `--config`. Conversion can replace
same-provenance drafts; inspect changes and continue the normal workflow gates.
Downloads do not change persisted findings/statuses or approve deployment.
Pending choices are browser-memory-only and are lost on refresh. Export is an
explicit user action; there is no local write server, external chart library,
automatic mapping choice, or external runtime dependency.

Optional browser regression tests use an already installed Playwright/browser:
set `SENTINEL_REPORT_BROWSER_TESTS=1`, optionally
`SENTINEL_REPORT_BROWSER_CHANNEL=chrome`, then run
`python -m unittest discover -s Tools/SentinelToXDRMigration/tests -p test_report_review_browser.py`.

### Run context and rule details

Run profile, stage states, workspace configuration presence, and recorded shared
messages appear once. A missing result is **evidence unavailable**, not proof of
a skipped check. **Not required** comes only from recorded workflow state.
Individual failures, blocked results, measured zero rows, and exceptions remain
visible even when a run-level stage is not required. Historical stage messages
are retained separately from current artifact counts.

**Ready for validation** requires a converted rule, passed local structural
checks, no recorded rule review flag/failure, and a recorded passed conversion
stage. This is not deployment approval or proof of semantic equivalence.
Automated successes remain **Readiness unconfirmed** while conversion review
is incomplete; unmapped semantic findings in workflow evidence are not silently
treated as resolved. These are presentation labels only: the dashboard never
changes gates, source statuses, or the existing JSON summary contract.

The compact rule list shows problems and next actions. Details retain warnings,
review reasons, entity recommendations, check results, and original diagnostics.
Identical inherited conversion/structural findings are grouped per rule, retaining
their stages and raw evidence; shared findings show affected-rule counts rather
than inflated occurrence totals. Categories are navigation aids, not semantic
validation. Source and converted KQL are visible immediately when a rule's Details
opens, alongside an offline unified text diff. These are current file snapshots at
report generation, not a claim of query equivalence or a historical content
snapshot. Reports omit empty package-resource inventory and consent panels when no
decision was recorded; populated inventory and substantive approval, denial, or
stale-consent evidence remain visible. No external scripts, fonts, services, or new
dependencies are used. Theme follows the system preference or
`?scoutTheme=light` / `?scoutTheme=dark`.

Outputs:

```text
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\migration-report.json
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\migration-report.html
```

## Deploy Custom Detections

Deployment uses the documented Microsoft Graph beta Custom Detection API. The
API is preview and requires delegated `CustomDetection.ReadWrite.All` consent
plus an appropriate Defender XDR or Entra security role.

Authenticate once:

```powershell
sentinel-xdr-migration setup-deployment `
  --solution "Solutions\<solution>" `
  --tenant-id "<tenant-id>"
```

This uses Azure CLI browser authentication by default. Device-code and direct
browser credential flows are also available:

```powershell
sentinel-xdr-migration setup-deployment `
  --solution "Solutions\<solution>" `
  --tenant-id "<tenant-id>" `
  --auth-method browser
```

Optionally run the read-only Qualification preflight with an explicitly
selected cached credential for diagnostic evidence:

```powershell
sentinel-xdr-migration preflight-deployment `
  --solution "Solutions\<solution>" `
  --auth-method azure-cli `
  --run-id "<run-id>"
```

The preflight requires the `CustomDetection.ReadWrite.All` management
permission in the acquired token, reported as a delegated `scp` or an
application `roles` claim. For Azure CLI it requests a Graph resource token
with `https://graph.microsoft.com/.default`; that resource request does not
prove the permission is present, so the token claims are inspected separately.
Missing permission claims or malformed claim values are reported as unknown.
A delegated `CustomDetection.Read.All` grant may support the preflight's
read-only exact-rule check, but does not satisfy deployment's required
management permission. These exact-ID existence reads are optional
pre-deployment diagnostics and do not establish ownership or deployment
readiness.

The report separates `managementPermissionGrant` from `readAccess`,
`effectiveRole`, and `writeAuthorization`. A successful exact-rule `GET`
confirms only read access. This command does not create or update rules,
request consent, start login, or switch credential methods. Run
`setup-deployment` separately when cached authentication or consent must be
established.

**Current backend limitation:** `preflight-deployment` still performs
per-detection exact-ID reads and may report denied reads as blocking. The
standalone preflight may be omitted when no other Qualification step requires
it, but the optional mock-ingestion stage uses it for DCR/permission checks and
cannot skip its bundled exact-ID reads. The Graph deployment command also
performs its own exact-ID `GET` to choose `POST` versus `PATCH`, then requires
read-back verification. These backend reads cannot be skipped through
documentation; do not bypass them with direct API calls. The Sentinel
deployment command instead uses `PUT` to the deterministic
`Microsoft.SecurityInsights/alertRules/{ruleId}` resource, which creates or
updates the alert rule without a separate existence check. The Sentinel
Alert Rule Template API is a read-only catalog and is not created by this
route; package `contentTemplates` installation is a separate route. Graph
`POST` itself is not documented here as an idempotent upsert.

Deploy every structurally valid, fully converted detection:

```powershell
sentinel-xdr-migration deploy --solution "Solutions\<solution>"
```

Rules are always submitted as disabled. The command creates missing rules,
updates matching client-provided IDs, and writes
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\deployment.graph.json`.

### Delegated Graph client and guarded app registration

The built-in Graph client remains the default. To use a separately registered
public desktop client for Custom Detection deployment, first review the exact
registration plan for the locked solution tenant:

```powershell
sentinel-xdr-migration plan-delegated-app-registration `
  --solution "Solutions\<solution>" `
  --app-display-name "Sentinel-XDR-CustomDetection"
```

The optional `--app-display-name` is bound into the plan hash and must be
identical when registering. If omitted, the generic
`Sentinel-XDR-CustomDetection` name is used. The plan above
describes one single-tenant public client named exactly
`Sentinel-XDR-CustomDetection`, the `http://localhost` redirect, and only the
delegated Microsoft Graph `CustomDetection.ReadWrite.All` permission. It does
not create an application or grant consent. The registration route requires
separate delegated bootstrap scopes `AppRegistration.Create` (create) and
`User.Read` (enumerate only the signed-in user's owned applications) and
explicit app-registration approval. These are used only by the bootstrap
authentication; they are not added to the Custom Detection app, whose only
requested permission remains `CustomDetection.ReadWrite.All`. Authenticate
explicitly, then submit the exact plan hash and approval:

```powershell
sentinel-xdr-migration setup-app-registration-auth `
  --solution "Solutions\<solution>" `
  --auth-method device-code `
  --bootstrap-client-id "<existing-public-Graph-client-id>"

sentinel-xdr-migration register-delegated-app `
  --solution "Solutions\<solution>" `
  --app-display-name "Sentinel-XDR-CustomDetection" `
  --expected-plan-sha256 "<plan-sha256>" `
  --approve-exact-app-registration
```

The route checks the signed-in user's owned applications before creating
anything, reuses only one exact matching owned app, and stops on multiple,
inaccessible, or differently configured matches. It never retries an
uncertain create, modifies an existing app, creates a service principal,
creates a client secret, requests admin consent, or grants application
permissions or ARM/Defender roles. The permission declaration is not consent
or proof that the permission is effective. An administrator must separately
review and grant the required consent; the deployment preflight remains
responsible for reporting token claims, read access, and write authorization
as distinct evidence. If the bootstrap scopes cannot expose enough details to
verify the operator's owned applications, registration stops before creating
an app rather than requesting broader directory permissions.

Delegated Microsoft Graph token checks treat each operation's configured
scopes as minimum requirements: all required scopes must appear in a valid
delegated `scp` claim, while additional valid names are reported as
`extraScopeNames` and do not fail the scope check. This includes incidental
OpenID Connect names such as `email`, `openid`, and `profile`; their presence
does not mean the toolkit requested them or broadened consent. Missing or
malformed `scp`, application-role-only tokens, a wrong tenant, or a non-Graph
audience remain blocked. Client and authentication-purpose binding,
operation-specific minimums, and existing read, write, and exact-resource
approval gates remain unchanged.

If the bootstrap `User.Read` owned-object response omits application settings,
use the separate read-only reconciliation route. It uses a distinct
`appReadback` authentication purpose, private auth record, and token cache;
the already-approved public client may be reused, but bootstrap credentials
are never implicitly reused. The route requests only delegated `User.Read`
and `Application.Read.All`, enumerates the signed-in user's owned applications,
then reads the exact approved application. It performs Graph GET requests only
and completes local private configuration only after ownership, tenant, IDs,
display name, audience, localhost redirect, and the sole delegated
Custom Detection permission all match.

```powershell
sentinel-xdr-migration setup-app-readback-auth `
  --solution "Solutions\<solution>" `
  --readback-client-id "<existing-public-Graph-client-id>"

sentinel-xdr-migration verify-delegated-app-readback `
  --solution "Solutions\<solution>"
```

Authentication is an explicit browser sign-in. Missing consent, token claims,
ownership, or settings leave reconciliation incomplete; the command does not
create or modify an application, grant consent, or fall back to app creation.

If readback is blocked because a required token scope is missing, this diagnostic uses
only the existing private readback credential and the explicitly selected
Qualification run:

```powershell
sentinel-xdr-migration diagnose-app-readback-scopes `
  --solution "Solutions\<solution>" `
  --run-id "<exact-qualification-run-id>"
```

It disables interactive authentication, may refresh the cached token
non-interactively, and makes no Microsoft Graph resource request or private
configuration change. It reports normalized expected, actual, missing, and
extra scope names only; satisfying the required scopes does not perform the
readback GET or prove ownership, application settings, or Graph access. Missing
required scopes remain blocked. The application settings check remains exact:
the readback GET must show precisely the approved delegated
`CustomDetection.ReadWrite.All` and `ThreatHunting.Read.All` permissions.

#### Manual existing-app permission update

The currently recorded Qualification app is shared by Advanced Hunting and Custom
Detection only after its exact two-scope configuration has been verified.
Inspect the offline plan:

```powershell
sentinel-xdr-migration plan-delegated-app-permission-update `
  --solution "Solutions\<solution>"
```

The plan binds the approved tenant, application/client ID, object ID, display
name, previously approved Custom Detection-only permission set, exact desired
two-scope set, and plan hash. It is manual-only: the documented Microsoft
Graph [Update application API](https://learn.microsoft.com/graph/api/application-update?view=graph-rest-1.0)
does not specify server-enforced conditional replacement of
`requiredResourceAccess`. A fresh GET or process lock cannot prevent another
owner from changing the property before PATCH, so the toolkit provides no
automated PATCH route. If manual work is needed, add only delegated
`ThreatHunting.Read.All`, preserve `CustomDetection.ReadWrite.All`, and do not
add roles, credentials, or request consent. Then use the separate readback
credential:

```powershell
sentinel-xdr-migration verify-delegated-app-permission-update `
  --solution "Solutions\<solution>" `
  --expected-plan-sha256 "<plan-sha256>"
```

This verifier performs GETs only. Legacy one-scope settings return
`manual-update-required`; extra or otherwise mismatched settings remain
blocked. Exact verification selects the same app client ID independently for
Custom Detection and Advanced Hunting, but preserves purpose-specific auth
records, caches, tenant/client bindings, and minimum-scope checks. An app
permission declaration or successful readback does not prove that a later
Advanced Hunting token contains `ThreatHunting.Read.All`; authenticate and
validate that purpose separately.

For this localhost-redirect Custom Detection app, use browser authentication
when setting up its deployment credential:

```powershell
sentinel-xdr-migration setup-deployment `
  --solution "Solutions\<solution>" `
  --auth-method browser `
  --custom-detection-client-id "<application-id>"
```

The approved registration payload does not enable the fallback public-client
flow used for device-code authentication. Browser authentication is required
for this Custom Detection app. Consent remains a separate administrator
action.

Use `--overwrite` to replace previously generated files. Without it, the
converter refuses to overwrite a file whose content differs.

## Optional migration configuration

Create `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/migration-config.yaml` when a solution needs explicit
table, function, or column rewrites:

```yaml
schemaVersion: 1.0.0
tableMappings:
  LegacyTable_CL: CurrentTable_CL
functionMappings:
  LegacyParser: CurrentParser
columnMappings:
  LegacyTable_CL:
    UserName: AccountUpn
```

Mappings are applied token-by-token. Time-column handling is table-aware:
native Defender tables use `Timestamp`, while verified Sentinel workload
tables such as `AzureActivity` retain `TimeGenerated`. Rewrites skip quoted
strings and line comments. Runtime validation is authoritative for tables and
KQL constructs exposed through the unified Advanced Hunting surface.

Conversion does not require queries to mention or return `Timestamp` or
`TimeGenerated`, and does not add either column to satisfy a local check.
[Microsoft's custom detection guidance](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules)
recommends event-time columns for alert timing; when they are not projected,
alert first/last event times use the detection lookback window. This is not a
blanket conversion or structural-validation failure. Existing generated YAML
retains its recorded conversion errors until explicitly regenerated; historical
reports are not rewritten by this policy change.

Entity mappings are checked against columns plausibly produced by `project`,
`extend`, `summarize`, `distinct`, `parse`, and `mv-expand`. The analyzer
deliberately over-approximates output rather than blocking queries it cannot
prove invalid. High-confidence Account, Host, IP, URL, and Azure resource
columns can be repaired or inferred when source mappings are incomplete.

The generated file declares `resourceType:
Microsoft.Security/detectionRules`. A later packaging milestone can consume
this field and the `apiVersion`/`properties` block without reinterpreting the
source analytic rule.

## Agent skills

Repository-native skills under `.github/skills/` teach compatible agents how
to invoke this utility:

- `sentinel-xdr-end-to-end-orchestrator`
- `sentinel-xdr-rule-converter`
- `sentinel-xdr-detection-validator`
- `sentinel-xdr-migration-orchestrator`
- `sentinel-xdr-solution-packager`
- `sentinel-xdr-solution-deployer`
- `sentinel-xdr-alert-parity-validator`

The repository also provides one user-facing custom agent:

```text
.github/agents/sentinel-xdr-migration.agent.md
```

Select **Sentinel XDR Migration** from the host's agent picker. The agent uses
the top-level orchestrator skill, which delegates to the specialist skills
while the CLI remains the source of deterministic behavior and persisted
workflow state.

The skills call the CLI through the agent's normal terminal tools. They contain
no credentials and do not host a custom MCP server.

The canonical agent-neutral contract is:

```text
Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md
```

Thin adapters are provided for:

- generic agents through `AGENTS.md`;
- GitHub Copilot through `.github\agents` and `.github\skills`;
- Claude Code through `CLAUDE.md` and
  `.claude\skills\sentinel-xdr-migration\SKILL.md`;
- Cursor through `.cursor\rules\sentinel-xdr-migration.mdc`; and
- Windsurf through `.windsurf\rules\sentinel-xdr-migration.md`.

All adapters point to the same workflow and deterministic CLI. They must not
fork the stage definitions or make optional qualification mandatory.

Microsoft's official Sentinel Triage MCP can optionally provide Advanced
Hunting schema and execution tools:

`https://sentinel.microsoft.com/mcp/triage`

It is not required. The utility remains usable without MCP, and missing runtime
access never blocks offline conversion or structural validation.

## Logging

Runtime logs and reports are written below `Data/`:

- `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/sentinel-xdr-migration.log`
- `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/manifest.json`
- `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/runtime-validation.graph.json`

These files are local execution artifacts and are ignored by Git.

## Tests

```powershell
python -m unittest discover -s Tools\SentinelToXDRMigration\tests -p "test_*.py"
```

## Planned milestones

- approved live Defender Workbook contract and query/UI qualification evidence;
- solution migration dashboard;
- optional retrieval-assisted guidance for schemas, prior art, and historical
  findings.
