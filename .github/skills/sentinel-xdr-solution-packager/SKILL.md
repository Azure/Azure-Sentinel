---
name: sentinel-xdr-solution-packager
description: Package a complete Microsoft Sentinel and Defender XDR solution through the V3.1 packaging implementation.
---

# Package a Sentinel and Defender XDR solution

Use this skill after solution content, any `XDR Detections/*.yaml`, and selected
`XDR Workbooks/*.json` files are complete and structurally validated.

The XDR Solution Manager workflow always runs V3.1. Legacy V3 remains available outside
this workflow for legacy Sentinel-only packaging and intentionally ignores XDR
Detections. Never use V3 to satisfy this workflow's packaging stage.

The generated package remains a full Microsoft Sentinel solution. When XDR
Detections are declared, it also supports hybrid installation:

- `DeployAnalyticsRule=true` (default) installs Sentinel Analytic Rule content.
- `DeployCustomDetection=true` (default false) installs Custom Detections and their
  Content Hub registrations independently. Both selections may be true.
- Custom Detections are always packaged disabled.
- `DeployDefenderWorkbook=true` (default false) installs Defender Workbooks and
  their registrations independently of Sentinel `DeployWorkbook`.

## Defender Workbook candidate boundary

Use the explicit solution Data `XDR Workbooks` selection. An empty array emits no
Defender Workbook resources or deployment flag; never scan to repopulate it.
Each selected file retains a complete `Notebook/1.0`, distinct canonical content
and installation GUIDs, exact raw source-file and query provenance, resolved
prerequisites, and explicit false review markers. Content versions inherit the
selected solution release; the Notebook format version is unchanged.

Installation and stored installation templates carry exactly the resolved
package/content identity quartet. Full registration also retains prerequisites.
Reviewed workspace functions are declared in `requiredWorkspaceFunctions` with
`functionAlias`, solution-relative `sourcePath`, and current `sourceSha256`.
Required parser installation is mandatory: the workbook's outer installation
deployment must depend on the actual unconditional
`Microsoft.OperationalInsights/workspaces/savedSearches` resources emitted in
the same enclosing template. Do not substitute parser catalog registration for
installation, invent dependencies on external resources, or allow selection
flags to skip required parsers. Missing/stale/ambiguous prerequisites block
packaging before template mutation. Parser overwrites are expected for this route.
Keep workspace-function prerequisites in full registration; installed content
provenance remains the quartet. ARM ordering does not prove AH visibility or
query/runtime acceptance.
Do not classify `_GetWatchlist` as an installable parser or `Watchlist` as
connector-fed telemetry. Raw reference lineage is separate from required
workload/connector data types.
Do not rewrite source workbooks, remove panels, silently resolve blockers, or
treat conversion findings as permission to change toolkit implementation.

The installation/registration provider contract is unverified. A generated
candidate is not accepted packaging. Require independent approved lab
installation, registration/provenance readback, repeat-install and update
evidence before claiming contract acceptance. ARM success, ARM-TTK, and local
tests do not establish workbook UI or query qualification. No packaging command
implicitly authorizes environment writes.

## Scope

This skill:

- validates the solution-data packaging contract for both Sentinel-derived and native XDR Custom Detections;
- selects and applies one semantic version increment;
- runs the supported local packaging entry point (`package-v3-1`) and `arm-ttk` validation;
- verifies the generated template, parameter file, and ZIP;
- checks per-file provenance rules (AR-to-CD matching for Sentinel-derived detections; standalone registration for native detections) and hybrid deployment conditions; and
- reports validation failures without hiding or weakening them.

It does not convert Analytic Rules, create mock data, deploy the generated
template, enable detections, or validate alert parity.

## Inputs

- A solution folder under `Solutions\`.
- The solution data folder, normally `Solutions\<solution>\Data`.
- The version action: `none`, `patch`, `minor`, or `major`.

Use `none` for repeat local validation. Before producing a package intended for
submission, ask which release increment to apply. Never bump the version more
than once for the same package attempt.

V3.1 requires effective solution release versions in `[3.2.0, 4.0.0)`.
Independent XDR Custom Detection release versions remain in `[3.1.0, 4.0.0)`.
Other content release versions must be below `4.0.0`; their
legacy lower versions remain valid. Out-of-range versions are hard errors, not
automatic promotions. A major bump from `3.x` is therefore rejected.
XDR requires its own top-level YAML `version` (`major.minor.patch`); new
conversions and native detections initialize it to `3.1.0` (or the solution release version in `[3.1.0, 4.0.0)`) independently of any Sentinel source.
Registration metadata and content product IDs use that value. This check
applies regardless of deployment selection. Data `XDR Detection Version`, solution
version, and source provenance are not fallbacks. Older files missing the
version must be explicitly reconverted with `--overwrite` after reviewing
manual edits, or have their independent XDR version authored. Never falsify
`contentProvenance.source.version` or bump the source AR to satisfy the XDR floor.
Solution version bumps do not change per-detection versions.
These bounds do not apply to API, schema, or extension-provider versions.

## XDR packaging contract

When the solution contains Custom Detections, confirm its solution-data JSON
declares `"XDR Detections"` (with `"Analytic Rules"` optional when a solution packages only native XDR Custom Detections):

```json
{
  "Analytic Rules": [],
  "XDR Detections": []
}
```

For every XDR Detection YAML, require:

- `kind: CustomDetection`;
- top-level `version` in `[3.1.0, 4.0.0)`, separate from `schemaVersion`;
- `resourceType: Microsoft.Security/detectionRules`;
- a supported `apiVersion`;
- a stable `properties.id`;
- `contentProvenance.requiredWorkloads` and `contentProvenance.requiredDataConnectors` (with `dependencyReviewRequired: false` allowed once dependencies are reviewed and populated);
- per-file provenance mode:
  - **Sentinel-derived detections** (migrated from `Analytic Rules/*.yaml`): must include both `contentProvenance.source` (with `id` matching a packaged Analytic Rule and `querySha256`) and `contentProvenance.conversion`; validated with `MIG-V01` and AR↔CD parity checks;
  - **Native / directly authored detections** (standalone under `Solutions/<Solution>/XDR Detections/*.yaml`): omit `contentProvenance.source` (and `querySha256`) and `contentProvenance.conversion` without requiring a source `Analytic Rules/` YAML; skip `MIG-V01` and AR↔CD parity checks and run target structural, KQL (without Sentinel workspace parser aliases), runtime, dependency, and V3.1 packaging checks;
- a query, schedule, alert template, and reviewed entity mappings; and
- `properties.status: disabled`.

For Sentinel-derived detections, `properties.id` is `xdr-<full source GUID>`,
while `contentProvenance.source.id` remains the original unprefixed GUID. For native detections without `contentProvenance.source`, `properties.id` in the authored YAML is the detection's own stable `xdr-<uuid>`. The
packager normalizes a bare GUID on its packaging copy if encountered, keeps a canonical
`xdr-` ID unchanged, and rejects unrelated custom IDs; it must not rewrite the
authored detection YAML or provenance. Installation and registration IDs and
references must use the same normalized identity. Existing deployed identities
are not migrated or deleted. An optional read-only identity review may help
diagnose known legacy IDs or collisions, but it is not a mandatory
pre-deployment existence check. Follow the canonical toolkit-owner managed
update policy: approved same-ID workbook and XDR detection overwrites are normal,
including in labs. Do not require a previous remote-content hash match or an
extra overwrite decision solely because existing content/version differs.
Stop for wrong or ambiguously mapped identities and out-of-scope resources,
not for an intended managed same-ID update. Personalized workbook copies use
separate IDs and are not selected for toolkit updates. Preserve deployment
consent, disabled detection payloads and exact post-write acceptance checks.

`Include XDR Content Registration` is deprecated: any supplied value warns and
is ignored. V3.1 emits installation and registration together under
`DeployCustomDetection`; live provider support for registration is **unverified**.
Do not claim otherwise from template generation. Require separate exact-scope
approval before any environment write.

## Offline ISV `authoring` route (`arm-ttk`)

Partners and authors packaging native or converted XDR Custom Detections without live tenant, MCP, or Graph credentials can use the explicit offline ISV `authoring` workflow profile (`--workflow-profile authoring`), which runs:

1. Target structural and KQL validation (`sentinel-xdr-migration validate`);
2. V3.1 packaging (`sentinel-xdr-migration package-v3-1`); and
3. Repository `arm-ttk` template validation on the generated `Package/mainTemplate.json` and `Package/createUiDefinition.json`.

## Workflow

1. Work from the repository root.
2. Confirm PowerShell 7.1 or newer, Node.js, and the `powershell-yaml` module are
   available. Install missing dependencies only after confirming they are
   required.
3. Inspect the solution-data JSON and all referenced files. Stop on missing,
   duplicate, conflicting, or review-required content.
4. For every Sentinel-derived detection (`contentProvenance.source` present), verify `contentProvenance.source.id` resolves to a packaged Analytic Rule content ID. For every native detection (`source` and `conversion` omitted), verify `contentProvenance.requiredWorkloads` and `contentProvenance.requiredDataConnectors` are populated.
5. Confirm the current solution version and the requested bump. Check that
   `ReleaseNotes.md`, when present, can be synchronized to the resulting
   version.
6. Run the deterministic toolkit wrapper:

   ```powershell
   sentinel-xdr-migration package-v3-1 `
     --solution ".\Solutions\<solution>" `
     --version-bump none
   ```

   Use `none` for validation without modifying source versions. Replace it with
   the approved `patch`, `minor`, or `major` value when producing a release
   package; those options update the solution data and metadata versions. The
   wrapper invokes
   `Tools\Create-Azure-Sentinel-Solution\V3\createSolutionV3_1.ps1` with local
   version mode, validates every required output and the ZIP, and writes
   `Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\packaging.v3_1.json`.

   Never reuse pre-existing package artifacts as proof that this stage ran.
   Complete the workflow stage only with the wrapper's `workflowArtifacts`
   values, including `packager=V3.1` and `packageReport`.
   Historical V4 reports are not V3.1 evidence; rebuild rather than relabel them.

   Optional `trackingId` in SolutionMetadata.json must contain the complete ID
   copied unchanged from Partner Center > offer > plan > Technical configuration.
   Never synthesize it or substitute a bare GUID, Partner ID, or plan ID.
   If absent or blank, packaging continues without a marker and nested XDR
   packages warn that Partner Center cannot auto-add attribution for functional
   nested deployments. Surface that warning and recommend adding the ID and
   rebuilding; do not claim upload rejection.
   See [official attribution guidance](https://learn.microsoft.com/partner-center/marketplace-offers/azure-partner-customer-usage-attribution#microsoft-marketplace-azure-apps).

7. Require successful packaging and inspect:

   - `Package\mainTemplate.json`;
   - `Package\createUiDefinition.json`;
   - `Package\testParameters.json`; and
   - `Package\<version>.zip`.

8. For a hybrid or standalone XDR package, verify:

   - only emitted families declare `Deploy*` booleans; Sentinel defaults true,
     `DeployCustomDetection` defaults false, and UI/test parameters agree;
   - every AR is gated by `DeployAnalyticsRule`, independently of CDs;
   - every CD installation and registration is gated by `DeployCustomDetection`;
   - existing conditions are AND-composed without changing nested scopes;
   - every Sentinel-derived CD resolves to one source AR, while native CDs package and register standalone without a source AR; CD deployment/registration counts match;
   - every CD body has `status: disabled`;
   - deployment names and CD IDs are unique and deterministic;
   - content packages and attribution remain unconditional; dependencies are
     unchanged and may still require unselected content or external prerequisites;
   - no `E5Flavor` or `RegisterE5Content` parameter is generated;
   - multiple authored tactics retain only the first authored entry and its
     techniques in both ARM payload copies, with an explicit omission warning;
     authored YAML and provenance remain unchanged, and Graph deployment still
     has its single-tactic guard; and
   - the generated ZIP version matches the solution-data version.

9. Run the repository packaging validations (including `arm-ttk` template checks). Do not classify skipped tests as
   passed. Separate genuine template failures from documented validator or
   environment limitations.
10. Report the generated version, artifact paths, content counts, validation
    results, and any deployment prerequisites or unresolved failures.

Packaging is complete only when the artifacts exist, versions are synchronized,
all expected resources are present, the V3.1 evidence report is accepted by the
workflow gate, and no unexplained validation failure remains.
