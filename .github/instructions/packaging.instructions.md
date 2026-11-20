---
applyTo: "Solutions/**"
---

# Solution Packaging & Validation Instructions

## Overview

When asked to **build**, **package**, **validate**, or **qualify** a Microsoft Sentinel solution—including a hybrid Microsoft Sentinel + Defender XDR solution—follow an **agentic-first** workflow:
1. **Inspect** `Data/Solution_*.json`, `SolutionMetadata.json`, `ReleaseNotes.md`, and any `Logs/sentinel-xdr-migration/*/workflow-state.json` first.
2. **Select or resume** the workflow via `XDR Solution Manager` / `sentinel-xdr-migration` (`qualification` profile by default, or `authoring` explicitly when no live lab is available) for any hybrid solution; use legacy `build-and-validate.ps1` directly only as a Sentinel-only fallback.
3. **Execute** the deterministic packaging (`createSolutionV3_1.ps1` / `package-v3-1`) and validation (`build-and-validate.ps1 -SkipPackaging`) backends, keeping all workflow gates intact.

| Solution content | Packaging route |
|------------------|-----------------|
| Legacy Sentinel-only content, with no XDR content to package | `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1`, through the combined build script |
| Hybrid content containing Custom Detections (`XDR Detections`) and/or Defender Workbooks (`XDR Workbooks`), including workbook-only solutions | `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3_1.ps1`; use `sentinel-xdr-migration package-v3-1` for a migration workflow |
| Historical V4 packages/reports | **Never use V4 for this workflow.** Retain historical evidence and rebuild with V3.1; never relabel it |

V3.1 also packages the solution's selected Sentinel content. Legacy V3
intentionally skips XDR Detections and is not a hybrid packaging route. The local
build runner still calls legacy V3; it does **not** auto-select V3.1.
For migration workflow stages, selections, approvals, and acceptance gates, follow
`Tools/SentinelToXDRMigration/agent-workflows/end-to-end-migration.md` and the
toolkit README. These instructions do not replace those gates.

## Agentic-First Workflow (Default)

When a user asks to **build**, **package**, **validate**, or **qualify** a solution via GitHub Copilot (CLI or IDE):

1. **Prefer the `XDR Solution Manager` agent / `sentinel-xdr-migration` (`qualification` profile by default)** for any hybrid Sentinel + Defender XDR solution (or use `authoring` explicitly when no live lab is available). Use legacy `build-and-validate.ps1` directly only for Sentinel-only solutions with no XDR content.
2. **Inspect before asking:** Read `Data/Solution_*.json`, `SolutionMetadata.json`, `ReleaseNotes.md`, and any existing `Logs/sentinel-xdr-migration/*/workflow-state.json` first, so you can resume active runs without re-asking settled questions.
3. **Batch unresolved confirmations in one shot:** After inspecting persisted state and current input identity, batch only unresolved decisions (reuse settled profile and approved release actions without re-asking). Default new workflows to `qualification` (explicit `authoring` fallback). For a new V3.1 release, confirm a bump whose resulting version is `>= 3.2.2` and `< 4.0.0`, or a canonical target in that range with `none`. Validation-only runs and eligible consumed-action retries require no new version decision. Keep immediate exact-scope write approval separate from this initial batch.
4. **Keep deterministic work in repo tools:** Never hand-build `mainTemplate.json`, `createUiDefinition.json`, ZIPs, or validation reports—always invoke `sentinel-xdr-migration` / `createSolutionV3_1.ps1` and `build-and-validate.ps1 -SkipPackaging`.
5. **Natural-language entry examples for users:**
   - *"Package and qualify `Solutions/<Name>` using V3.1 in qualification mode."*
   - *"Resume packaging `Solutions/<Name>` with a `patch` bump and run validation."*

## How to Build a Solution

### Before Running the Script

**Always inspect persisted state and confirm unresolved version actions BEFORE running the script.** For new Sentinel-only releases without an explicit bump, ask:

> What type of version bump should this be?
> - **patch** — bug fixes, minor text changes, no new content
> - **minor** — new content added (rules, connectors, playbooks, etc.) or significant updates
> - **major** — breaking changes, major restructuring, or initial release (Sentinel-only V3; V3.1 hybrid releases must remain `>= 3.2.2` and `< 4.0.0`)
>
> (Default is `patch` if you're unsure.)

Only proceed once you have a clear answer (or the user explicitly says to use the default). Use the confirmed value for `-VersionBump`. Validation-only runs (`-SkipPackaging -VersionBump none`) and eligible consumed-action retries require no new version decision.

For V3.1, confirm the release action once through the selected workflow; reuse settled decisions without re-asking. The resulting solution version must be **`>= 3.2.2 and < 4.0.0`**, including no-bump rebuilds. An older version is not silently promoted. An explicitly approved target (for example, `--target-version 3.2.2 --version-bump none`) is supported by the migration CLI; the direct V3.1 script uses `-TargetVersion 3.2.2 -VersionBump none`. Never combine a target with a non-`none` bump or increment twice on retry. For changed inputs or retries, follow the canonical release-action/freshness checks rather than bypassing them with `none`.

**Always tell the user what's about to happen BEFORE you run the script:**

> 🔄 Running full build & validation suite for **{SolutionName}** with a **{VersionBump}** version bump. This typically takes **3-5 minutes** — it compiles the validation runtime, runs scoped .NET tests, ARM-TTK (30 template checks), and hyperlink validation. I'll present the complete report when it finishes.

This message MUST appear in your chat response BEFORE you execute the script. The user needs to know the agent is working, not frozen.

### Single Command (Recommended for Legacy Sentinel-Only Solutions)

From the repository root, run:

```powershell
pwsh .script/local-validation/build-and-validate.ps1 `
  -SolutionName "<Solution Folder Name>" `
  -VersionBump "<confirmed-patch-minor-or-major>" `
  -ReleaseNotes "<description of changes>"
```

### V3.1 Packaging (Hybrid Solutions)

Before packaging, verify the explicit content selections and current review
evidence described in Step 1 below. For an existing migration workflow, resume
its exact run and use the supported CLI route:

```powershell
# Example: the selected run's approved release action is already consumed,
# and its current input identity permits a no-bump build.
sentinel-xdr-migration package-v3-1 `
  --solution "Solutions/<Solution Folder Name>" `
  --run-id "<run-id>" `
  --version-bump none

# Validate that exact V3.1 output; do not let the wrapper package again.
pwsh .script/local-validation/build-and-validate.ps1 `
  -SolutionName "<Solution Folder Name>" `
  -SkipPackaging `
  -VersionBump none `
  -PackageReportPath "Logs/sentinel-xdr-migration/<run-id>/packaging.v3_1.json" `
  -ValidationSkip ""
```

Use the run's approved bump or target instead of `none` for its first release
action. For a separate toolkit checkout, pass `--toolkit-root "<toolkit-root>"`
to `package-v3-1`; invoke that toolkit's validation script with
`-ContentRoot "<content-repository-root>"`.

Direct V3.1 PowerShell invocation (`createSolutionV3_1.ps1`) is a raw artifact-generation backend, not a workflow packaging or acceptance route, and **does not emit `packaging.v3_1.json`**. For package-bound validation, have `XDR Solution Manager` initialize or resume the selected workflow, invoke `sentinel-xdr-migration package-v3-1`, and pass its exact returned `packaging.v3_1.json` path to `build-and-validate.ps1 -SkipPackaging`. Never fabricate a report for direct-script output or substitute a different run's receipt.

Keep the selected ARM validation method consistent. For a `lab-deployment`
candidate, add `-ArmValidationMethod lab-deployment` to the validation command;
this replaces **only ARM-TTK** with pending external lab validation and requires
`-SkipPackaging`, `-PackageReportPath`, and the remaining applicable checks.
It is not a shortcut to acceptance. For an explicitly selected offline
Authoring ARM-TTK route, use `arm-ttk`. Defender Workbooks additionally require
the independent installation/registration and repeat-install/update evidence
specified by the canonical workflow; ARM-TTK alone cannot establish that
contract. Missing provider/authentication evidence remains a blocker, not a
reason to bypass it or assert readiness.

**⚠️ Never run the wrapper without `-SkipPackaging` after V3.1.** Its default
legacy V3 step can overwrite the hybrid output. `-VersionBump none` alone does
not prevent packaging. Keep version/release-note preparation separate from
validation-only mode, which writes neither.

### Examples (Sentinel-Only Fallback Backend)

```powershell
# Exact name
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection"

# Partial name — auto-resolves if only one match
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "1Password"

# Partial name with multiple matches — script lists options, ask user to pick
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "Palo Alto"
```

### Solution Name Resolution

The `-SolutionName` parameter supports **partial/fuzzy matching** — the user does NOT need to know the exact folder name:

- **Exact match** → used directly
- **Single fuzzy match** (e.g., `"1Password"`) → auto-resolved, proceeds automatically
- **Multiple matches** (e.g., `"Palo Alto"`) → script exits with a numbered list of matching solutions

**When multiple matches are returned (exit code 2):**
1. Present the list to the user and ask which one they meant
2. Re-run the script with the exact name the user picks
3. Do NOT guess — always let the user choose

**Example interaction:**
- User says: *"Build Palo Alto solution"*
- You run: `pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "Palo Alto"`
- Script outputs:
  ```
  ⚠️  Multiple solutions match 'Palo Alto':
    1. Palo Alto - XDR (Cortex)
    2. Palo Alto Cortex XDR CCP
    3. Palo Alto Prisma Cloud CWPP
    4. PaloAltoPrismaCloud
  ```
- You ask the user: *"I found 4 Palo Alto solutions — which one?"* and present the list
- User picks one → you re-run with the exact name

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `SolutionName` | Yes | — | Full or partial solution name — supports fuzzy matching (see below) |
| `VersionBump` | No | `patch` | Version increment: `none`, `patch`, `minor`, or `major`; use `none` with validation-only mode |
| `ReleaseNotes` | No | — | Description of what changed. **Always provide this when the wrapper packages** — it updates `ReleaseNotes.md`; ignored for updates in validation-only mode |
| `SkipValidation` | No | `$false` | Skip the validation step (packaging only) |
| `SkipPackaging` | No | `$false` | Skip the packaging step (validation only); **mandatory after V3.1** |
| `ValidationSkip` | No | `kql,detection-schema,non-ascii,arm-ttk` | Comma-separated validators to skip |
| `ContentRoot` | No | Toolkit checkout | Repository checkout containing the selected solution content; use with `-SkipPackaging` for cross-worktree validation |
| `EvidenceDirectory` | No | `.script/local-validation/Logs` | Ignored evidence parent under the toolkit checkout; each run writes a unique folder |
| `PackageReportPath` | No | — | Exact V3.1 report under the selected solution; requires `-SkipPackaging` and forbids `-SkipValidation`; emits hash-bound package validation evidence |
| `ArmValidationMethod` | No | `arm-ttk` | `arm-ttk` or `lab-deployment`; the latter leaves ARM validation pending and requires a package-bound validation-only run |

### Validate Content From Another Checkout

The script and all validators/dependencies are loaded from the checkout containing
`build-and-validate.ps1`. To validate current (including uncommitted and untracked)
content from a separate checkout, pass its canonical Git root explicitly and require
validation-only mode:

```powershell
pwsh /path/to/toolkit/.script/local-validation/build-and-validate.ps1 `
  -SolutionName "CiscoASA" `
  -ContentRoot /path/to/content-checkout `
  -SkipPackaging `
  -VersionBump none `
  -ValidationSkip "" `
  -EvidenceDirectory ".script/local-validation/Logs/cisco-validation"
```

`-ContentRoot` must be a Git worktree root containing `Solutions/`; the selected
solution must be a real, direct child of that checkout's `Solutions/`. A separate
content checkout is rejected unless `-SkipPackaging` is supplied. TypeScript
compilation, validator scripts, .NET projects, validation configuration, and ARM-TTK
helpers remain rooted in the toolkit checkout; solution-specific file discovery and
the scoped PowerShell validators use the selected content checkout. Repository-wide
secret scanning remains skipped because it cannot be scoped to one solution.

The ignored evidence run folder contains complete TypeScript JSON results,
TypeScript stdout/stderr and compile output, combined captured child output for .NET,
PowerShell, and ARM-TTK validators, and the complete build report. A missing or
malformed structured TypeScript report is a validation failure, not an empty success.
Skipped validators remain reported as skipped. No package, solution-data, or release
notes are written in cross-checkout validation-only mode.

## What Happens During Build

### Step 1: Packaging (V3 or V3.1)

For legacy Sentinel-only builds, the script calls `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1` which:
- Reads the solution data file (`Solutions/{Name}/Data/Solution_*.json`)
- Collects all content (data connectors, parsers, analytics rules, playbooks, workbooks, etc.)
- Generates `mainTemplate.json` and `createUiDefinition.json` in the `Package/` folder
- Creates a versioned ZIP file (e.g., `3.3.4.zip`)

For hybrid builds, V3.1 uses the selected Sentinel content plus the explicit
`XDR Detections` and `XDR Workbooks` arrays in
`Solutions/{Name}/Data/Solution_*.json`. For example, these entries belong in
the existing solution data object, not a separate XDR manifest:

```json
{
  "Version": "3.2.2",
  "Analytic Rules": ["Analytic Rules/Example.yaml"],
  "XDR Detections": ["XDR Detections/Example.yaml"],
  "Workbooks": ["Workbooks/Example.json"],
  "XDR Workbooks": ["XDR Workbooks/Example.json"]
}
```

This is an illustrative fragment; retain all required solution metadata and
other content selections. Every selected path must resolve to existing content
within the solution. Do not select reports, receipts, or operational files.
An explicit empty XDR array selects none; never repopulate it by scanning a
folder. Existing XDR files with a missing explicit selection must be resolved
through the supported selection workflow before packaging.

**Custom Detections:**
- Select deployable YAML under `XDR Detections`, with `kind: CustomDetection`,
  `resourceType: Microsoft.Security/detectionRules`, valid IDs, independent
  content versions, and reviewed workload/connector dependencies.
- Each selected detection must match exactly one packaged originating Sentinel
  AnalyticsRule content template. Do not drop that source selection or invent
  an originating rule. Workbook-only solutions need no invented detections.
- V3.1 emits disabled detection installation through the `MicrosoftSecurity`
  extension and Content Hub `CustomDetection` registration together under
  `DeployCustomDetection`. The old `Include XDR Content Registration` property
  is deprecated and ignored, including when set to `false`.
- Preserve the generated `E5Flavor`/content-selection conditions, source IDs,
  unique canonical target IDs, and disabled status. Verify counts against the
  reviewed selections, not all files present in the folders.
- Package projection uses the first authored tactic and compatible techniques;
  retain complete authored YAML/provenance and disclose the classification
  loss. Package generation does not establish alert or classification parity.

**Defender Workbooks:**
- Select complete `Notebook/1.0` JSON under `XDR Workbooks`; retain the source
  Sentinel `Workbooks` independently. Authored `xdrMetadata` has distinct
  canonical content and stable installation GUIDs.
- V3.1 emits `Microsoft.Security/workbooks@2026-06-01-preview` installation
  through the `MicrosoftSecurity` extension plus Content Hub `DefenderWorkbook`
  registration. Both use **`DeployDefenderWorkbook=false` by default**,
  independent of Sentinel `DeployWorkbook`.
- Deployment copies omit `xdrMetadata` and replace authoring provenance with
  `packageId`, `packageVersion`, `contentId`, and `contentVersion`. Registration
  additionally retains reviewed public dependencies. Installed workbook
  `contentVersion` uses the selected solution release; publication cleanup
  does not change the authored workbook version.
- Required workspace functions must have current reviewed source hashes,
  selected parser definitions, and unconditional saved-search installation.
  The workbook installer depends on the actual emitted parser resources.
  Installation order is not proof of query visibility or runtime correctness.

V3.1 produces `Package/mainTemplate.json`, `createUiDefinition.json`, the
parameter file, and versioned ZIP. Verify these against the current
`packaging.v3_1.json` evidence, with `packager=V3.1`, before claiming packaging
success. A candidate is not accepted packaging or a deployment. XDR content
requires valid customer usage attribution: a missing `trackingId` triggers
Marketplace lookup even with offline skip controls. Lookup failure or ambiguity
blocks packaging; verify the offer or supply the complete Partner Center ID
unchanged. Never synthesize an ID or use a skip flag to bypass this requirement.

#### Defender Workbook Publication Receipts

Published workbook JSON must use **`contentProvenance.format:
public-workbook-v1`**, factual origin, and compact public workload, connector,
and workspace-function dependencies. Keep reviewer accounts, acceptance
decisions, references, session context, query inventories, conversion proof,
and reverse-delta history out of published JSON.

Normal authoring and packaging require a **current whole-document hash-bound
local receipt**. For each reviewed legacy/migration/import artifact, use the
supported publication sequence:

```powershell
$Solution = "Solutions/<Solution Folder Name>"
$Content = "XDR Workbooks/Example.json"
$ReviewDirectory = Join-Path $Solution "Logs/workbook-reviews"
New-Item -ItemType Directory -Force $ReviewDirectory | Out-Null
$Plan = Join-Path $ReviewDirectory "publication-plan.json"
$Review = Join-Path $ReviewDirectory "publication-decisions.json"

sentinel-xdr-migration workbook-publication-plan `
  --solution $Solution --content $Content |
  Set-Content -LiteralPath $Plan -Encoding utf8

# Inspect the exact file and complete dependency plan. Save a reviewed copy
# as $Review with explicit nonempty actor/reference and decision "accept".
# Do not auto-approve, edit inputSha256, or invent missing connector coverage.
$Decision = Get-Content -LiteralPath $Review -Raw | ConvertFrom-Json
sentinel-xdr-migration workbook-publication-clean `
  --solution $Solution --content $Content --review $Review `
  --expected-sha256 $Decision.inputSha256
sentinel-xdr-migration workbook-publication-validate `
  --solution $Solution --content $Content --mode authoring
```

Cleanup checks the original hash and historical evidence, retains the original
artifact/proof verbatim locally, and changes only `contentProvenance`.
Notebook content, queries, IDs, and authored version remain unchanged. Missing
connector/table coverage must be explicitly reviewed and completed; historical
exceptions are not publication waivers.

The clean/update tools create receipts consumed automatically by current
document hash. Keep them and their supporting evidence under ignored
`Logs/workbook-reviews`; do not hand-author receipts. Any later query, setting,
metadata, or dependency change requires fresh explicit review.
`workbook-publication-validate --mode structural` checks portable structure
without private approvals; it does **not** replace `--mode authoring`.

**Never commit or force-add solution `Logs/`.** Receipts, private reviews,
workflow state, and raw evidence are not deployable content or ZIP inputs.
Keep published JSON clean rather than embedding local evidence to make another
checkout pass. The README documents a separate, explicit published-commit
reproduction route; that route is not authoring acceptance and must not be used
to bypass local receipt requirements.

### Step 1.5: Version Sync & Release Notes

For the combined legacy V3 route, the script reads the generated version after
packaging and defers its source-data/release-note writes until after validation:

**Version sync** — Updates the `"Version"` property in `Solutions/{Name}/Data/Solution_{Name}.json` to match the new version from the generated package. This keeps the source data file in sync with what was packaged.

**Release notes** — If `-ReleaseNotes` was provided, updates `Solutions/{Name}/ReleaseNotes.md`:
- Reads the **new version** from the generated `mainTemplate.json`
- Inserts a new row at the top of the release notes table with the version, today's date, and the change description
- If `ReleaseNotes.md` doesn't exist, creates it with the proper header
- If `-ReleaseNotes` was not provided, prints a warning

**You MUST always provide `-ReleaseNotes` when the wrapper packages.** To determine what changed:
1. **Ask the user** what they changed, OR
2. **Check `git diff`** against the target branch to summarize the changes yourself
3. Keep it concise but descriptive (1-2 sentences)

Good examples:
- `"Added new RTEM data connector with 19 event types"`
- `"Updated CrowdStrike API connector to fix rate limit exceptions"`
- `"Added Cortex XDR playbook for automated incident response"`

Bad examples:
- `"Updated solution"` (too vague)
- `"Changes"` (useless)

For V3.1, use the approved release action to synchronize solution data and
metadata versions. Prepare the release-note row for that exact release under
`.github/instructions/releasenotes.instructions.md` before final package
acceptance. Neither the direct V3.1 entry point nor `package-v3-1` accepts the
wrapper's `-ReleaseNotes` parameter; passing it to a later `-SkipPackaging` run
does not update release notes. A post-build input edit can stale the package:
use the canonical approved release-note refresh/rebuild route, not an extra
version bump or a hand-edited package.

### Step 2: Local Validation

The script first runs `npm run tsc` to regenerate the ignored JavaScript runtime from the current TypeScript sources, then runs `node .script/local-validation/validate.js --path Solutions/{Name}` which checks. If compilation fails, it reports the error and does not run potentially stale JavaScript.

#### ✅ Runs Locally (13 validators — same code as GitHub CI)

| Validator | What It Checks |
|-----------|---------------|
| **JSON syntax** | All JSON files parse correctly |
| **YAML syntax** | All YAML files parse correctly |
| **Data connector schema** | Connectors match their category schema (26 types) |
| **Content branding** | No "Azure Sentinel" text (must be "Microsoft Sentinel") |
| **Logo validation** | SVG format, ≤5KB, valid content |
| **Sample data** | Emails sanitized to `sanitized@sanitized.com` |
| **Playbook validation** | ARM template schema, parameters, metadata, resources |
| **Workbook template** | Schema URI, version, template ID, resource info |
| **Workbook metadata** | Schema, unique keys, image existence, version increment |
| **Documents link** | No locale codes in Microsoft documentation URLs |
| **Solution validation** | Domains/verticals, support object, branding, solution ID |
| **ID change detection** | Template IDs must not change (uses local `git diff`) |
| **ARM-TTK** | ARM template best-practice testing (PowerShell — runs in Step 3) |

### Step 3: .NET Validators & ARM-TTK (Detection Schema, Non-ASCII, KQL, ARM-TTK)

After the TypeScript validators, the script runs 3 additional .NET test projects plus the ARM-TTK PowerShell validator:

| Validator | Runtime Required | Scope | What It Checks |
|-----------|----------------------|-------|---------------|
| **Detection Schema** | .NET Core 3.1 | **Solution only** — runs tests matching the solution's Analytic Rules files | Detection/analytics rule schema compliance — required fields, string lengths, entity mappings, connector IDs, no duplicate template IDs |
| **Non-ASCII** | .NET Core 3.1 | **Solution only** — runs tests matching the solution's content files | Scans scoped solution YAML/JSON files for non-ASCII characters (outside `U+0000`–`U+007F`) |
| **KQL** | .NET 8.0 | **Solution only** — runs tests matching the solution's Analytic Rules, Hunting Queries, Parsers, and Data Connectors | KQL query syntax validation using the Sentinel KQL analyzer |
| **ARM-TTK** | PowerShell | **Solution only** — validates Package/mainTemplate.json and Package/createUiDefinition.json | ARM template best-practice testing using the [Azure ARM-TTK](https://github.com/Azure/arm-ttk) module. Runs `Test-AzTemplate` with the same tests and exemptions as `.github/actions/entrypoint.ps1`; both load `.script/package-automation/arm-ttk-sentinel-filters.ps1`. Module auto-clones from GitHub on first run (to `.arm-ttk/`, gitignored). |

**How solution scoping works:** The .NET test projects may enumerate repository paths during test discovery, but filters restrict which tests execute to the selected solution's files. File discovery is separate from validation scope.

Detection Schema test cases expose only file basenames. If a selected rule has a duplicate or filter-sensitive basename, that validator is reported as skipped with the reason instead of risking validation of another solution's rule.

The selected solution folder is the scope for all solution-specific checks. The TypeScript runner and PowerShell children inspect current files in that folder (including uncommitted and untracked files; deleted files are absent), rather than selecting a solution from the latest commit. The folder must be an existing direct child of `Solutions/`. TruffleHog scans repository history and is explicitly skipped because it cannot be scoped to one solution. When the PowerShell scripts are invoked without a solution folder, their existing CI commit-diff behavior is preserved.

### Step 4: CI PowerShell Validators & Secret Scanning

After the .NET validators, the script runs 4 additional checks that mirror GitHub CI workflows:

| Validator | CI Workflow | What It Checks | Requirements |
|-----------|-------------|----------------|--------------|
| **Field Types** | `validateFieldTypes.yaml` | Validates the selected solution's current `Package/mainTemplate.json` | `powershell-yaml` module |
| **Classic App Insights** | `validateClassicAppInsights.yaml` | Detects deprecated classic App Insights resources in current `azuredeploy` files under the selected solution | `powershell-yaml` module |
| **Hyperlink Validation** | `hyperlinkValidator.yaml` | Validates URLs in current files under the selected solution — checks for 404s, 500s, broken links | `powershell-yaml` module, **network access** |
| **TruffleHog (Secrets)** | `ScanSecrets.yaml` | Repo-history secret scan; skipped for folder-scoped validation because it cannot be limited to one solution | `trufflehog` CLI (external tool) |

For folder-scoped validation, the Classic App Insights check for standalone `DataConnectors/` is also explicitly reported as skipped because it is outside the selected solution folder.

**Important notes:**
- Folder-scoped validation inspects current solution files instead of inferring a solution from the latest commit. With no explicit folder scope, the PowerShell scripts preserve their CI commit-diff behavior.
- **Hyperlink Validation** is slow — it makes HTTP requests with a 20-second timeout per URL. It requires network connectivity and will be skipped if the network is unavailable.
- **TruffleHog** is optional — it requires the `trufflehog` CLI to be installed ([install guide](https://github.com/trufflesecurity/trufflehog#installation)). If not installed, it is skipped with a message.
- The 3 PowerShell validators require the `powershell-yaml` module; the script auto-installs it if missing.

**Runtime detection:** The script checks whether the .NET SDK command is executable,
then independently checks the exact target runtimes required by the test projects:
- If **.NET Core 3.1** is available → runs Detection Schema and Non-ASCII (both scoped)
- If **.NET 8.0** is available → runs KQL validator (scoped to solution)
- If the `dotnet` SDK command is unavailable, all three .NET validators are skipped
  with an SDK-unavailable message. An installed SDK does not imply that its target
  runtime is installed.
- If a required target runtime is **missing** → only that validator is skipped with a message:
  ```
  ⏭  Detection Schema validation skipped — .NET Core 3.1 runtime not installed.
     Install it from: https://dotnet.microsoft.com/download/dotnet/3.1
  ```
- **ARM-TTK** uses the ARM-TTK PowerShell module to run `Test-AzTemplate` — the same checks as `.github/actions/entrypoint.ps1`, sharing `.script/package-automation/arm-ttk-sentinel-filters.ps1`: no tests are skipped, only exact Sentinel content-identifier properties (`id`, `contentProductId`, `packageId`, `fromTemplateId`, `chartId`, `columnId`) and `customDetails` `*Id` column names are exempt from the resource-ID test, and blanks are allowed only inside workbook payloads (classic `serializedData`, Defender workbook `properties.content`). The module auto-clones from GitHub on first run (stored in `.arm-ttk/`, gitignored). If the `Package/` folder exists, ARM-TTK runs automatically.
- If the solution has **no relevant content files** (e.g., no Analytic Rules) → skips with:
  ```
  ⏭  Detection Schema validation skipped — no Analytic Rules found in <SolutionName>.
  ```

## Prerequisites

Before building, ensure:

1. **Node.js 16+** is installed
2. **npm dependencies** are installed: `npm install` (from repo root)
3. **TypeScript is compiled**: `npx tsc` (from repo root)
4. **PowerShell 7+** is installed (for the V3/V3.1 packaging scripts)
5. **.NET Core 3.1 runtime** — required for Detection Schema and Non-ASCII validators ([download](https://dotnet.microsoft.com/download/dotnet/3.1))
6. **.NET 8.0 runtime** — required for KQL validator ([download](https://dotnet.microsoft.com/download/dotnet/8.0))
7. **Git** — required for ARM-TTK module auto-clone on first run and for Step 4 CI validators

> **Note:** Items 5 and 6 are optional. If the required .NET runtime is not installed, those validators will be skipped with a message. The remaining validators will still run.

8. **`powershell-yaml` module** — required for Step 4 CI PowerShell validators (auto-installed if missing)
9. **Network access** — required for Hyperlink Validation (skipped if unavailable)
10. **TruffleHog CLI** — optional, for secret scanning ([install](https://github.com/trufflesecurity/trufflehog#installation))
11. **For V3.1 workbook authoring/packaging:** Python **3.11 or 3.12** and the migration toolkit dependencies are required. `SENTINEL_XDR_PYTHON` selects the interpreter used by the PowerShell workbook validator; otherwise it uses `python`. Missing dependencies or receipts are errors, not validation waivers.

## Validation Only (Without Packaging)

To run just the validation checks:

```powershell
# Validate a specific solution
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection" -SkipPackaging -VersionBump none

# TypeScript-only diagnostics (not a substitute for the full official runner)
node .script/local-validation/validate.js --path "Solutions/CrowdStrike Falcon Endpoint Protection"

# Validate with JSON output (for programmatic consumption)
node .script/local-validation/validate.js --path "Solutions/CrowdStrike Falcon Endpoint Protection" --json
```

After V3.1 packaging, use the package-bound `-SkipPackaging` command above.
With `-PackageReportPath`, the runner emits `build-and-validate-binding.json`
beside its report, binding the selected solution, current package report and
artifact hashes, and before/after input and package fingerprints. Missing,
stale, or changed evidence fails validation. Preserve the complete report and
binding; structural success alone is not live provider acceptance.

## Sample User Commands

These are example prompts a user might type in their agent (GitHub Copilot, Cursor, Windsurf, etc.). For each, follow the workflow described above.

### Build / Package a Solution

The legacy examples below apply only after checking the packaging-route table.
For XDR content, substitute the V3.1 workflow and then validate with
`-SkipPackaging`; do not follow a legacy example that would overwrite it.
All release builds still require the confirmed version action and release notes.

| User Says | What You Do |
|-----------|-------------|
| *"Build V3 solution for CrowdStrike"* | Ask the user what changed (or check `git diff`), then run with `-SolutionName "CrowdStrike" -ReleaseNotes "<description>"`. If multiple matches, present the list and ask user to pick. |
| *"Package the Palo Alto solution"* | Run with `-SolutionName "Palo Alto"`. Multiple matches expected — present list, let user choose. Then ask what changed for release notes. |
| *"Build 1Password with a minor version bump"* | Ask what changed, then run with `-SolutionName "1Password" -VersionBump minor -ReleaseNotes "<description>"`. |
| *"Create a new package for Salesforce Service Cloud"* | Ask what changed, then run with `-SolutionName "Salesforce Service Cloud" -ReleaseNotes "<description>"`. |
| *"Rebuild the CrowdStrike solution — I added a new RTEM connector"* | User already described the change. Run with `-SolutionName "CrowdStrike" -ReleaseNotes "Added new RTEM data connector"`. |
| *"Package Cisco solution as a major release"* | Run with `-SolutionName "Cisco" -VersionBump major`. Multiple matches likely — ask user to pick AND describe changes. |
| *"Package this hybrid solution with Custom Detections and XDR Workbooks"* | Use `XDR Solution Manager` / `sentinel-xdr-migration`; inspect existing state, resume the explicitly selected run, default new runs to `qualification`, and follow the next gated stage (`workflow-next`). |

### Validate Only (No Packaging)

For hybrid V3.1 solutions, route validation through `XDR Solution Manager` / `sentinel-xdr-migration` using the current run's exact `-PackageReportPath` and recorded `-ArmValidationMethod`. The legacy examples below apply to Sentinel-only solutions:

| User Says | What You Do |
|-----------|-------------|
| *"Validate the CrowdStrike solution"* | Run with `-SolutionName "CrowdStrike" -SkipPackaging`. |
| *"Run validations on Palo Alto Prisma Cloud CWPP"* | Run with `-SolutionName "Palo Alto Prisma Cloud CWPP" -SkipPackaging`. |
| *"Check if my solution passes CI checks"* | Ask which solution, then run with `-SkipPackaging`. |
| *"Validate all JSON files in the Fortinet solution"* | Run with `-SolutionName "Fortinet" -SkipPackaging`. |

### Package Only (No Validation)

These examples are legacy Sentinel-only routes and do not waive the validation
requirement before a PR. A V3.1 candidate must still follow the separate official
validation/acceptance route; never use legacy `-SkipValidation` packaging for it.

| User Says | What You Do |
|-----------|-------------|
| *"Just package the Okta solution, skip validation"* | Run with `-SolutionName "Okta" -SkipValidation`. |
| *"Generate the mainTemplate for Qualys"* | Run with `-SolutionName "Qualys" -SkipValidation`. |

### Troubleshooting

| User Says | What You Do |
|-----------|-------------|
| *"The build failed, what's wrong?"* | Read the error output. If validation failed, show the specific checks that failed with file paths. If packaging failed, check the Data folder and Solution JSON for issues. |
| *"Which solutions do we have for Palo Alto?"* | Run with `-SolutionName "Palo Alto" -SkipPackaging -SkipValidation` to trigger the fuzzy match list, then present results. |
| *"List all available solutions"* | Run `Get-ChildItem Solutions/ -Directory \| Select-Object Name` from the repo root. |

## Inline Build Report

After all steps complete, the script emits a **structured report** to stdout between `[REPORT_START]` and `[REPORT_END]` markers.

**⚠️ MANDATORY — You MUST show the COMPLETE report before responding:**

1. **The script takes 3-10 minutes.** This is normal — it runs .NET tests, ARM-TTK, hyperlink checks, etc.
2. **Track the invoked process and its printed evidence directory** under `.script/local-validation/Logs/`. While it runs, report meaningful progress and any approval/blocker requests without claiming completion.
3. **After termination**, if output was truncated or missing `[REPORT_END]`, read that invocation's `build-and-validate-report.md` inside its printed evidence run directory. If execution exited early before creating a report (for example on a configuration failure), present its exit code and captured error immediately — do not wait for missing markers or substitute another run's report.
4. Present the full report in your chat response — the text between `[REPORT_START]` and `[REPORT_END]`
5. Do NOT summarize, paraphrase, or abbreviate the report — show it in full
6. If a validator failed, add your own analysis and fix suggestions **after** the report block

**NEVER tell the user to "check the terminal."**

The report includes:
- **Header** — solution name, version change, date, total duration
- **Step 1** — packaging result, package file path, version sync status, release notes status
- **Step 2** — TypeScript compilation and per-validator pass/fail/skip counts with error details for failures
- **Step 3** — .NET validator results with test counts, durations, and scoping info
- **Step 4** — CI PowerShell validator results (field types, classic App Insights, hyperlinks, TruffleHog)
- **Summary** — overall pass/fail status with totals across all validators
- **Evidence paths** — full structured results and captured child output under the ignored run folder

For V3.1 validation-only runs, the wrapper correctly reports packaging as
skipped; report the preceding V3.1 packaging evidence separately. Do not
interpret this as missing hybrid content or rerun legacy packaging. If lab ARM
validation is pending, retain that pending result and distinguish candidate
generation, local validation, installation/registration acceptance, and runtime
qualification.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Packaging + validation both succeeded |
| `1` | Packaging or validation failed (check output for details) |
| `2` | Configuration error (solution not found, missing dependencies, etc.) |

## Important Rules

- **Always validate after packaging.** Never submit a PR with unvalidated packages.
- **Do not modify files** in `.script/utils/`, `.script/tests/`, or `.github/workflows/` — they are production code visible to external customers.
- **The `Package/` folder is auto-generated.** Its contents are created by the packaging script. Do not hand-edit `mainTemplate.json` or `createUiDefinition.json`.
- **Version bumping**: Use `patch` for bug fixes, `minor` for new features, `major` for breaking changes.
- **Hybrid packages use V3.1, never V4 or legacy V3.** The V3.1 solution release must remain `>= 3.2.2 and < 4.0.0`; a requested major bump to 4.x is not supported by this route.
- **Always pass `-SkipPackaging` when validating V3.1 output.** Bind evidence to the exact current report; do not consume another version action.
- **Workbook publication receipts stay local.** Keep clean public JSON and current authoring receipts separate; never commit `Logs/` or treat structural checks as review acceptance.
- **Packaging is not deployment or qualification.** Preserve disabled detections and generated default-off content controls. Environment writes need separate exact-scope approval and the canonical workflow's technical gates.
- **Do not patch tooling to recover from a failed build.** Record the blocker and require a separate maintainer change; never bypass version, selection, receipt, attribution, or validation gates.
