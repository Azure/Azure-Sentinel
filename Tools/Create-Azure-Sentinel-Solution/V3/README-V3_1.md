# Create Solution V3.1

`createSolutionV3_1.ps1` supports both local and GitHub pipeline invocation.
Both entry points live in the V3 directory:

- `V3\createSolutionV3.ps1` remains the legacy Sentinel-only local entry point.
- `V3\createSolutionV3_1.ps1` adds XDR Detection packaging, supports local use,
  and remains the CI entry point.

Both entry points use `common\commonFunctions.ps1` for the core packaging
implementation. Only V3.1 enables Defender XDR Custom Detection and Defender Workbook injection.

They are alternative entry points, not two required packaging steps. Use V3
for a legacy Sentinel-only package and V3.1 when the solution contains XDR
Detections. The repository pipeline runs V3.1 for PR/CI packaging.
The former `V4/createSolutionV4.ps1` entry point was renamed, not the legacy
`pipeline/createSolutionV4.ps1`. Package-version selection and
`contentSchemaVersion` are unchanged; the V3.1-only release-version guards below
reject out-of-range selections.

## Local usage

```powershell
.\Tools\Create-Azure-Sentinel-Solution\V3\createSolutionV3_1.ps1 `
  -SolutionDataFolderPath ".\Solutions\<solution>\Data" `
  -VersionMode local `
  -VersionBump none
```

The local parameter set calls `common\createSolutionLocal.ps1` directly. V3
uses the same common implementation through its own adapter; neither entry
point invokes the other.

Use `none` for repeat validation without changing source versions. Use
`patch`, `minor`, or `major` when preparing a release; those options persist
the new version into the solution data file and `SolutionMetadata.json`.

## Pipeline usage

In CI, V3.1 receives pipeline-calculated metadata and version parameters. The
package automation calls it through:

```text
.script\package-automation\package-generator.ps1
```

The 12 positional pipeline parameters (positions 0–11) are unchanged.
The optional named `-SkipAttributionLookup` switch is available in both local
and pipeline parameter sets. For CI callers that do not forward optional
arguments, set `SENTINEL_SKIP_ATTRIBUTION_LOOKUP=1` in the process environment.
Both controls apply only when attribution is optional; emitted XDR detections
or Defender Workbooks require attribution and cannot skip missing-ID lookup.

## Independent content selection (V3.1 default)

V3.1 local and pipeline output use independent ARM boolean `Deploy*` parameters,
including Sentinel-only solutions. Only families actually emitted receive a
parameter, UI checkbox/output, and `testParameters.json` entry. Legacy V3 keeps
its existing behavior and has no new flags.

For a solution carrying the five corresponding families:

| Parameter | Default | Selected resources |
|---|---|---|
| `DeployAnalyticsRule` | `true` | AnalyticsRule and AnalyticsRuleTemplate content |
| `DeployPlaybook` | `true` | Playbook/PlaybookTemplate, owned AzureFunction and LogicAppsCustomConnector assets |
| `DeployWorkbook` | `true` | Sentinel Workbook and WorkbookTemplate content |
| `DeployDataConnector` | `true` | DataConnector, ResourceDataConnector/ResourcesDataConnector, DataType, connector metadata and catalog resources |
| `DeployCustomDetection` | `false` | Both Custom Detection installation and Content Hub registration |
| `DeployDefenderWorkbook` | `false` | Both Defender Workbook installation and Content Hub registration |

`common/contentDeploymentParameters.json` is the shared vocabulary used by
generation, UI, Python artifact checks, and tests. HuntingQuery, InvestigationQuery,
Parser, Watchlist/WatchlistTemplate, Notebook, AutomationRule and SummaryRule have
their own `Deploy<Kind>` controls **when emitted**, not speculative empty controls.
Required workspace parsers declared by selected Defender Workbooks remain
unconditional prerequisites, independent of optional content-family selections.
Classification uses content kinds,
resource types and explicit emitter ownership, not display names, counts or
query text. Unclassified content fails with its resource name/type/kind.

For example, the relevant generated fragments are:

```json
"DeployAnalyticsRule": { "type": "bool", "defaultValue": true },
"DeployCustomDetection": { "type": "bool", "defaultValue": false }
```

```text
AnalyticsRule:        [parameters('DeployAnalyticsRule')]
CD install:          [parameters('DeployCustomDetection')]
CD registration:     [parameters('DeployCustomDetection')]
```

Both switches may be true or false independently. Selecting CDs does **not**
suppress Sentinel templates, disable existing rule instances, or remove them.
CDs remain packaged disabled. Existing resource conditions are AND-composed
with the selection; existing variables, names, IDs, versions, resource bodies,
dependency ordering and nested template scopes remain intact. Outer selections
are not injected into stored templates or inner-scope deployment templates.
The CD registration depends on its install wrapper and the package, never the
reverse. The language-version-2 XDR template and MicrosoftSecurity import are
unchanged.

The content package and customer usage attribution marker remain unconditional;
the legacy workspace query container is shared infrastructure with independently
gated children. Each packaged Custom Detection is appended to the content
package's `dependencies.criteria` as `kind: CustomDetection`, using the same
literal `contentId` and independent XDR `version` as its registration. Existing
Sentinel criteria retain their order and the package keeps `operator: AND`.
These catalog dependencies are unconditional even when
`DeployCustomDetection=false`; the deployment switch controls emitted resources,
not package inventory. All selections false is permitted: package-only
installation (plus shared infrastructure/attribution when present), not an
uninstall operation. There is no new all-off runtime check. A selection can
leave prerequisites unmet: the booleans do not rewrite dependency semantics,
guarantee Content Hub acceptance, or provision missing external dependencies.

### Native Defender Workbooks without a Sentinel parent

Already-native Advanced Hunting workbooks use the explicit
`native-workbook-plan` / `native-workbook-review` / `native-workbook-import` authoring route documented in
[the migration toolkit README](../../SentinelToXDRMigration/README.md#native-defender-workbook-authoringimport-no-sentinel-parent).
The raw source may be supplied under solution-local `Workbook Sources/Native/`
while running the authoring commands, but it need not be retained or shipped.
Select only the authored `XDR Workbooks` candidate; no duplicate source artifact
is packaged. `contentProvenance.origin: native-xdr` selects native review with
historical source path/hash and a canonical reviewed Notebook payload hash,
instead of migrated-source converter proof. It does not weaken the existing
migrated workbook contract.

The V3.1 emitter invokes the shared native Python validator before any template
mutation, requiring Python 3.11/3.12 with the toolkit dependencies.
`SENTINEL_XDR_PYTHON` selects the interpreter (default: `python`); the subprocess
uses this emitter's toolkit checkout, not another editable installation.
Unknown functions/tables, payload/query changes, and stale/incomplete reviews
block packaging. Source deletion after import does not invalidate a native
candidate.
Native and migrated entries share managed install/registration, independent
Sentinel selection, default-false `DeployDefenderWorkbook`, and the installed
provenance quartet. Native sources/reviews are not installed or ZIP entries.
No Sentinel workbook, converter receipt or runtime acceptance is required or
manufactured for the native authoring route. Provider acceptance still requires
the existing independent approved evidence.

### Defender Workbook parser prerequisites

Authored workbooks declare reviewed function prerequisites in
`contentProvenance.requiredWorkspaceFunctions`: each record contains the exact
`functionAlias`, packaged solution-relative `sourcePath`, and current
`sourceSha256`. V3.1 resolves these records to the actual top-level
`Microsoft.OperationalInsights/workspaces/savedSearches` resources, not parser
content templates. The outer Defender Workbook installation deployment adds
`dependsOn` edges to those resources, preserving its content-package dependency.
Required parser installation is mandatory and supports normal same-resource
updates. Missing, duplicate, conditional, or stale prerequisites are errors,
not dependencies on nonexistent resources or permission to skip a parser.

`_GetWatchlist` is a supported built-in, not an installable parser prerequisite.
Its `Watchlist` input is platform reference data: preserve raw lineage, but
reject it in connector-fed telemetry data types in required workload/connector
records.

Full workbook registration carries reviewed function prerequisites. Installed
notebook provenance remains exactly the package/content identity/version
quartet. Deployment ordering does not verify connected-workspace access, AH
propagation, nested optional vendor coverage, query correctness, or the preview
workbook provider contract. Reviewed Sentinel workspace functions can be used
in AH and workbooks; this does not make them supported in Custom Detection rules.

**Compatibility:** `E5Flavor` and `RegisterE5Content` are no longer generated.
Update external parameter files to use only controls declared by that package;
omitting a declared parameter uses its default, whereas explicit `false` skips
that family. A package without CDs declares no `DeployCustomDetection`. The
legacy Data key `Include XDR Content Registration`, whether absent, `true` or
`false`, no longer controls emission. When present it produces a deprecation
warning and is ignored: every packaged CD has both wrappers under the same
switch. Remove this obsolete key from future Data files.

`createUiDefinition.json` exposes the declared subset in **Content selection**.
`testParameters.json` retains the existing parameter-definition format (including
defaults), not ARM deployment `{"value": ...}` overrides. The migration CLI passes
no legacy E5 controls; its report records `deploymentParameters`, visible build
warnings and `customDetectionRegistrationSupport: "unverified"` for XDR packages.
Live provider support for CustomDetection registration is **unverified**.
Template emission and offline tests do not establish deployment/Marketplace
acceptance. Any subsequent environment write requires separate approval.

### Custom Detection content provenance

Authored YAML must contain `contentProvenance.requiredWorkloads` records with
`workload` and `dataTypes`, and `requiredDataConnectors` records with `connectorId`
and `dataTypes`. Supported workload values are `mde`, `mdo`, `mdi`, `mda`, `mdc`,
`entraid`, `purview`, `appgovernance`, `sentinel`, `mtp`. Malformed/missing arrays,
unknown workloads and explicitly unresolved dependency review block packaging.
The legacy `conversion.requiredWorkloads` strings are not used as dependency
records.

The packager resolves `packageId` and `packageVersion` from the current solution,
and `contentId`/`contentVersion` from the canonical packaged detection ID and
authored XDR version. It stamps the same four-key `contentProvenance` on the
installation resource and the registration's stored installation resource.
Resolved literals are used in inner-scope templates, not references to outer
variables. Registration properties contain that quartet plus the YAML
`requiredWorkloads` and `requiredDataConnectors` arrays. Dependencies are never
placed on the deployed Graph object. Authored YAML and source rules are not
mutated. These emitted contract fields remain subject to live provider
verification; offline tests are not registration/deployment acceptance.

### ARM-compatible identifiers and JSON strings

Graph rule/entity IDs, provenance `packageId`, and custom-detail column bindings
whose names end in `id` are emitted as constant ARM `if` expressions. These
preserve the exact string value, including apostrophes, without treating
non-Azure identifiers such as `ProjectId` or `ZoneId` as Azure resource IDs.
The projection is limited to these detection and provenance fields; resource
references elsewhere still undergo the normal ARM-TTK checks.

For packages containing Custom Detections, JSON string brace delimiters `{` and
`}` are written as Unicode escapes while `[` and `]` remain literal so ARM-TTK
raw-text expression checks see `[parameters(...)]` and `[variables(...)]`. JSON
decoding restores the same ARM expressions, KQL, and other values. This lets
ARM-TTK extract nested templates even when a query contains unmatched braces
inside a string or regex. No validation check is skipped, and authored files
remain unchanged.

### First authored tactic in V3.1 ARM payloads

Authored YAML may retain multiple tactics. V3.1 validates a supplied, nonempty
array of tactic objects, then selects the **first entry in authored order** on
a deep copy of deployment properties. Both install and registration get the
same single-entry array, with that entry's techniques/subtechniques and ordering
unchanged. No tactics are sorted, merged or reclassified, and no technique from
another entry is moved into the selected tactic. Omitted optional tactics remain
omitted; malformed supplied lists fail before output.

This restriction exists because the current Custom Detections beta API accepts
only one tactic. Remove it deliberately once the API supports multiple tactics;
there is no automatic future-capability detection. Authored YAML, original
Sentinel rules, source provenance and full authoring classification remain
unchanged. Every truncation emits `V3.1 TACTIC SELECTION:` with the selected first
tactic and all omitted tactics; the migration CLI displays and persists the
warning. This is an API payload restriction, **not** a user-reviewed recommended
classification or a claim of full tactic coverage. A single tactic passes through
unchanged without a truncation warning. Legacy V3 and direct Graph deployment
behavior are unchanged; the Graph single-tactic guard still applies.

## Operational and PR evidence exclusions

Solution content references must not include `Logs`, `Reports`, or `Evidence`
path components (case-insensitive, either slash separator). Local V3/V3.1 and
the V3.1 pipeline reject these references before processing content, including
legacy string-encoded content lists. The ZIP writer uses only
`mainTemplate.json` and `createUiDefinition.json`, never solution-directory
recursion. The migration CLI additionally checks ZIP entries for these folders.
Optional curated `Evidence/<run-id>` snapshots are PR review material, not
Marketplace content or resumable operational state.

## Content-count summary

Both V3.1 entry points include **XDR Detections:** followed by the number of
successfully packaged individual detections in the Basics description of
`createUiDefinition.json` and the content package's `descriptionHtml` in
`mainTemplate.json`. The count follows Analytic Rules and precedes Hunting
Queries; zero-count categories are omitted. For example:
**Analytic Rules:** 15, **XDR Detections:** 15, **Hunting Queries:** 15.

This is an inventory count, independent of enabled status or the content selections.
Deployment wrappers, content registrations, and customer usage attribution
markers do not add to it. The API/schema kind remains `CustomDetection`; the
separate Content selection step controls deployment, not inventory. Legacy V3 and
`pipeline/createSolutionV4.ps1` descriptions are unchanged.

## Release-version bounds (V3.1 only)

Sentinel-derived Custom Detections use `xdr-<full originating analytic rule
template GUID>` as `properties.id`; `contentProvenance.source.id` retains the
original unprefixed GUID. Packaging normalizes a bare originating GUID on its
packaging copy and leaves an already-prefixed ID unchanged. It rejects unrelated
custom IDs rather than silently replacing them. This contract applies when
provenance declares Microsoft Sentinel / AnalyticsRule or the
`sentinel-to-xdr-migration` converter; unrelated Custom Detection identity
contracts are unchanged. The normalized ID is used consistently by installation
and registration, including content IDs, catalog criteria, and references.
Authored YAML and source provenance remain unchanged. This changes local
artifacts only; reconcile previously deployed identities before any new
deployment. Both install and registration templates retain the existing
`[if(true(), '<ID>', '<ID>')]` wrapper around the inner detection ID.

V3.1 applies these hard guards in local, catalog, and positional pipeline modes:

| Release version | Accepted range |
|---|---|
| Effective solution/package version, even without XDR content | `>= 3.2.2` and `< 4.0.0` |
| Effective XDR Custom Detection content version | `>= 3.1.0` and `< 4.0.0` |
| Effective Defender Workbook `xdrMetadata.version` | Canonical `major.minor.patch` in `[3.1.0, 4.0.0)` |
| Ordinary Sentinel Workbook metadata content version | `< 4.0.0`, except allowlisted legacy upstream workbooks (`MicrosoftDefenderForOffice365detectionsandinsights` at `4.0.0`, `ThreatIntelligenceWorkbook` / `ThreatIntelligence.json` at `5.0.0`) |
| Every other packaged content-item release version | `< 4.0.0`; existing `1.x`/`2.x` versions remain valid |

Existing Sentinel Workbook content and metadata versions are retained unchanged;
they must remain `< 4.0.0` unless explicitly allowlisted for legacy upstream
workbooks that already shipped at `>= 4.0.0` (`MicrosoftDefenderForOffice365detectionsandinsights`
at `4.0.0` and `ThreatIntelligenceWorkbook` / `ThreatIntelligence.json` at `5.0.0`).
This exception does not relax arbitrary workbook versions or solution, Custom Detection,
or Defender Workbook release-version checks.

The guard reports the content type/path, effective version, and required range.
It never promotes versions automatically. Explicit local bumps are evaluated
before output: for example, `major` from `3.2.2` selects `4.0.0` and is rejected.
An older source solution may reach the supported range through an explicitly
approved target or bump: an explicit target of `3.2.2` (or `patch` from `3.2.1`) selects `3.2.2`, whereas a `patch`
that remains in `3.1.x` is rejected. This solution floor does not change
independent content, Notebook, schema, API or provider version checks.
All version checks run before generated JSON/ZIP files are overwritten. Local
bump persistence is deferred until version validation and package generation
succeed; rejected versions leave the source versions and existing outputs intact.
Pipeline Data `Version` and calculated package version must agree exactly.
The existing missing-solution-version default (`3.0.0`) is below the minimum and
is rejected; supply an appropriate version explicitly.

Checks reuse each generator's effective version rather than scanning arbitrary
`version` fields: analytic/hunting YAML version (default `1.0.0`); parser
`Function.Version` (default `1.0.0`); workbook metadata version; playbook
`hidden-SentinelTemplateVersion` (default `1.0`, also the effective default for
packaged custom APIs/function apps); connector UI metadata version (default
`1.0.0` only when metadata is absent); summary-rule version; watchlist solution
version; and CCF `DataConnectorCCFVersion` (fallback solution version), shared by
connector-definition and connections content. Missing/invalid effective versions
without an existing generator default fail rather than gaining a new default.
Non-XDR numeric release versions support existing two-to-four-component
representations; comparison does not rewrite the emitted value.

**Independent XDR version:** every XDR YAML must declare its own top-level
`version` as a `major.minor.patch` string in `[3.1.0, 4.0.0)`. New conversions
start at `3.1.0`, independently of Sentinel source versions such as `1.0.2`.
Regeneration preserves valid existing XDR versions for the same source rule;
it does not reset `3.1.1` or silently replace an invalid `4.0.0`.
`contentProvenance.source.version` remains the original Sentinel release.
The packager uses the XDR version for registration metadata and content product
IDs, regardless of the deprecated `Include XDR Content Registration` setting.
Data `XDR Detection Version`, solution version, and source provenance are not
fallbacks in V3.1. Missing or invalid XDR versions fail before package output.
For older files with no top-level version, review manual edits and explicitly
reconvert with `--overwrite` to initialize `3.1.0`, or author the independent
version. Never falsify provenance. A solution bump does not bump XDR versions.

These guards do not govern ARM `apiVersion`, `contentSchemaVersion`, ARM template
`contentVersion`, extension-provider versions, converter/schema versions, or
saved-search API revision numbers. Legacy `V3/createSolutionV3.ps1` and
`pipeline/createSolutionV4.ps1` retain their previous version behavior.

## Customer usage attribution

Set `trackingId` in the solution's **SolutionMetadata.json** to the
**complete customer usage attribution tracking ID** copied from Partner Center
**offer > plan > Technical configuration**, for example:

```json
"trackingId": "pid-399fb80b-c914-4257-b61e-91ab73733888-partnercenter"
```

This example is illustrative; do not copy it into an offer. Never synthesize an
ID, use a bare GUID, or substitute a Partner ID or plan ID. The packager accepts
full `pid-` identifiers, including non-GUID identifiers, validates literal ARM
deployment-name characters and the 64-character limit, and uses the supplied
string unchanged. This syntax check does not verify ownership or registration.

Local and pipeline packaging read this value from SolutionMetadata.json even
when the Data input already contains consolidated metadata. It is a
packaging-only setting, not a SecurityInsights RP metadata property.

When supplied, V3.1 adds exactly one root `Microsoft.Resources/deployments`
marker (API `2025-04-01`, mode `Incremental`) containing an empty template with
schema `https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#`,
contentVersion `1.0.0.0`, and `resources: []`. The root remains an implicit ARM
language-version-1 template with a resources array; functional XDR deployments
retain their nested language-version-2 templates. The marker is added after
metadata resource filtering and is included in mainTemplate.json and the ZIP.

If `trackingId` is absent, null, or blank, V3.1 automatically attempts to recover
it from the **published Marketplace template**:

1. An anonymous public GET to `https://catalogapi.azure.com/offers?api-version=2018-08-01-beta`
   filters on exact `publisherId` and `offerId` from the authoritative metadata.
   Exactly one matching offer and one applicable plan are required.
2. The plan must contain exactly one artifact with type `Template`, name
   `DefaultTemplate`, and one HTTPS URI. The packager downloads that JSON with
   another anonymous GET. This is **not the authenticated Partner Center API**;
   no Azure/Graph tokens, credentials, or interactive authentication are used.
3. The published ARM document must contain exactly one literal root `pid-`
   deployment with a valid complete ID and an unconditional, empty inline
   template (`resources: []`). Functional wrappers, linked templates, conditional
   markers, malformed documents and ambiguous markers are rejected. Root
   `resources` arrays and language-version-2 symbolic resource objects are
   supported; symbolic keys are not interpreted as deployment names.
4. After content/version preparation and before package output, the exact ID is
   persisted into the same `SolutionMetadata.json`, then emitted using the
   packager's current `2025-04-01` marker shape (not the published API version).
   Only the root JSON value is edited; other bytes, nested fields, Unicode,
   UTF-8 BOM and newline formatting are preserved. A same-directory atomic
   replacement checks the original snapshot for concurrent edits. A local
   read/write/conflict failure is a **hard error**, never a successful cache.
   Subsequent runs use the saved ID without lookup; local version bump saving
   rereads metadata and retains the ID.

An existing nonblank ID always wins and is validated without network access.
There is no fallback to `ocpSolutionId`, a catalog ID, GUID synthesis, or an
assumption that `offerId` equals `planId`. No plan-selection metadata field is
introduced: multiple applicable plans require manual review and an explicit ID.
Version catalog lookup and `GetPackageVersion` behavior are unchanged.

Attribution requests use a 20-second request/connection timeout and, on
PowerShell 7.4+, an explicit 20-second stalled-read timeout, with no retries or
redirects (continuous downloads are not capped at 20 seconds).
For packages emitting XDR detections or Defender Workbooks, attribution is
**required**. HTTP status, timeout, network/read, JSON, selection and marker
failures produce a classified, terminating `CUSTOMER USAGE ATTRIBUTION:` error
before package files or the ZIP are written, leaving metadata unchanged.
Verify the correct publisher/offer identity and unambiguous published plan/marker,
or supply the complete ID from Partner Center and rebuild. There is no
incomplete-package override. When attribution is optional (no emitted XDR
detections or Defender Workbooks), lookup failures retain the warning-only
behavior and continue **without** attribution or metadata changes.
A successful lookup logs publisher, offer,
plan ID, template URL (without query credentials), tracking ID and updated path
as `CUSTOMER USAGE ATTRIBUTION SOURCE:`. It is not reported as a warning.

For optional offline attribution, use `-SkipAttributionLookup` or set
`SENTINEL_SKIP_ATTRIBUTION_LOOKUP=1`; explicit IDs still emit markers.
Neither control suppresses lookup when required attribution has a missing ID.
A valid explicit ID avoids attribution network access even for required packages. Use
`-VersionMode local` as well to avoid the **independent** version-catalog lookup.
These controls do not disable other packaging prerequisites or validators.
The migration CLI inherits the same environment control, so no redundant CLI
flag is required. Its packaging report preserves lookup failures in `warnings`
and successful source messages in `attributionSources`.

Partner Center cannot automatically add tracking for functional nested
deployments. If required lookup cannot resolve an ID, packaging fails rather
than emitting a markerless package. Obtain the ID from offer > plan > Technical
configuration, add `trackingId`, and rebuild. This packaging guard is not a
claim about Marketplace upload rejection.
See [Microsoft Marketplace Azure apps customer usage attribution](https://learn.microsoft.com/partner-center/marketplace-offers/azure-partner-customer-usage-attribution#microsoft-marketplace-azure-apps).

The migration CLI uses `package-v3-1` and writes `packaging.v3_1.json` with
`packager: V3.1`. Old V4 reports are historical evidence, not V3.1 evidence:
rebuild rather than rename or edit old reports.

## Focused regression checks

From the repository root (Python 3.11/3.12, PowerShell 7, and `powershell-yaml`):

```bash
PYTHONPATH=Tools/SentinelToXDRMigration:Tools/SentinelToXDRMigration/tests python3.12 -m unittest test_content_deployment_parameters test_packaging test_workflow test_customer_usage_attribution test_version_policy test_xdr_description_counts test_detection_identity test_connector_metadata test_parser_bindings
```

The attribution tests exercise both local and positional pipeline entry points
with isolated synthetic solutions, verify generated JSON and ZIP contents, and
cover missing/invalid IDs and nested XDR preservation. Catalog/template requests
are mocked; optional test subprocesses disable lookup, so unit tests never depend
on live Marketplace availability or mutate real solution metadata. Cases include
automatic persistence/replay, explicit overrides, ambiguous identities/plans/
markers, required lookup despite both offline controls, terminating failures
before artifact output, optional offline behavior, byte preservation, local write
failures/concurrent edits and cached-ID retention during version bumps.
They stub the unrelated
full repository validators and isolate repository-root resolution. They do not
build existing solution packages, deploy to Azure, or prove Marketplace upload
acceptance. Version tests also cover boundaries, catalog-result guards, effective
defaults, local bumps, pipeline consistency, and rejection without source/output
mutation.
Converter tests cover independent XDR initialization, unchanged source provenance,
version preservation, explicit legacy reconversion, and invalid-version conflicts.
Description-count tests cover zero, one, and multiple XDR detections, mixed
inventories, deprecated registration true/false (both emit), attribution exclusion, Markdown/HTML and ZIP
consistency, failed generation without partial output, and unchanged legacy
descriptions. Formatter tests also cover XDR-only and trailing/empty categories;
actual XDR packaging still requires the matching source Analytic Rules.

Content-selection tests evaluate all 32 combinations of the five reference
switches against resource identities, existing-condition composition, nested
scope/body preservation, connector companions, playbook automation assets,
unknown-kind rejection, defaults and omission, local/pipeline and V3 isolation,
and declaration/UI/test-parameter agreement. Real mixed-family fixtures provide
workbook metadata at the existing repository-relative lookup location; that
pre-existing path resolution is not changed here. Tactic tests cover two/three
entries, reversed source order, single-tactic preservation, malformed input,
consistent deep-copied install/registration payloads, visible persisted warnings
and byte-for-byte unchanged authored inputs.

## Local parser names in Custom Detections

Before emitting CD installation and registration bodies, the shared packager renames
local KQL bindings that match the solution's parser names or aliases. Both bodies receive
the same query. Source YAML and native parsers are not edited. This also protects inputs
that were authored outside the migration converter.

For solutions with parsers, install Node.js and run
`npm ci --prefix Tools\SentinelToXDRMigration\kql` from the repository root.
The shared Microsoft KQL semantic helper preserves binding scope and rejects unsafe
rewrites rather than falling back to text replacement. See the migration-tool README's
"Local parser bindings" section for limits and regression commands.
