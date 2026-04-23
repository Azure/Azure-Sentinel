---
applyTo: "Solutions/**"
---

# Solution Packaging & Validation Instructions

## Overview

When asked to **build**, **package**, or **create** a Microsoft Sentinel solution, follow this two-step workflow:
1. **Package** the solution using the V3 packaging tool
2. **Validate** the packaged solution using the local validation runner

Both steps are combined in a single script. **Always run validation after packaging.**

## How to Build a Solution

### Before Running the Script

**Always tell the user what's about to happen BEFORE you run the script:**

> 🔄 Running full build & validation suite for **{SolutionName}**. This typically takes **3-5 minutes** — it runs 21 validators including .NET tests (34K+ files for Non-ASCII), ARM-TTK (30 template checks), and hyperlink validation. I'll present the complete report when it finishes.

This message MUST appear in your chat response BEFORE you execute the script. The user needs to know the agent is working, not frozen.

### Single Command (Recommended)

From the repository root, run:

```powershell
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "<Solution Folder Name>"
```

### Examples

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
| `VersionBump` | No | `patch` | Version increment: `patch`, `minor`, or `major` |
| `ReleaseNotes` | No | — | Description of what changed. **Always provide this** — it updates `ReleaseNotes.md` |
| `SkipValidation` | No | `$false` | Skip the validation step (packaging only) |
| `SkipPackaging` | No | `$false` | Skip the packaging step (validation only) |
| `ValidationSkip` | No | `kql,detection-schema,non-ascii,arm-ttk` | Comma-separated validators to skip |

## What Happens During Build

### Step 1: Packaging (V3)

The script calls `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1` which:
- Reads the solution data file (`Solutions/{Name}/Data/Solution_*.json`)
- Collects all content (data connectors, parsers, analytics rules, playbooks, workbooks, etc.)
- Generates `mainTemplate.json` and `createUiDefinition.json` in the `Package/` folder
- Creates a versioned ZIP file (e.g., `3.3.4.zip`)

### Step 1.5: Version Sync & Release Notes

After packaging succeeds, the script automatically:

**Version sync** — Updates the `"Version"` property in `Solutions/{Name}/Data/Solution_{Name}.json` to match the new version from the generated package. This keeps the source data file in sync with what was packaged.

**Release notes** — If `-ReleaseNotes` was provided, updates `Solutions/{Name}/ReleaseNotes.md`:
- Reads the **new version** from the generated `mainTemplate.json`
- Inserts a new row at the top of the release notes table with the version, today's date, and the change description
- If `ReleaseNotes.md` doesn't exist, creates it with the proper header
- If `-ReleaseNotes` was not provided, prints a warning

**You MUST always provide `-ReleaseNotes`.** To determine what changed:
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

### Step 2: Local Validation

The script runs `node .script/local-validation/validate.js --path Solutions/{Name}` which checks:

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
| **Non-ASCII** | .NET Core 3.1 | **Entire repo** — scans all YAML files | Scans all YAML files for non-ASCII characters (outside `U+0000`–`U+007F`) |
| **KQL** | .NET 8.0 | **Solution only** — runs tests matching the solution's Analytic Rules, Hunting Queries, Parsers, and Data Connectors | KQL query syntax validation using the Sentinel KQL analyzer |
| **ARM-TTK** | PowerShell | **Solution only** — validates Package/mainTemplate.json and Package/createUiDefinition.json | ARM template best-practice testing using the [Azure ARM-TTK](https://github.com/Azure/arm-ttk) module. Runs `Test-AzTemplate` with the same skips and error filters as `.github/actions/entrypoint.ps1`. Module auto-clones from GitHub on first run (to `.arm-ttk/`, gitignored). |

**How solution scoping works:** The .NET test projects scan the entire repo during test discovery (this is unavoidable — it's built into the test data providers). However, `dotnet test --filter` restricts which tests actually **execute** to only those matching files in the target solution. This turns a 30+ minute full-repo validation into a fast, focused check.

### Step 4: CI PowerShell Validators & Secret Scanning

After the .NET validators, the script runs 4 additional checks that mirror GitHub CI workflows:

| Validator | CI Workflow | What It Checks | Requirements |
|-----------|-------------|----------------|--------------|
| **Field Types** | `validateFieldTypes.yaml` | Validates parameter field types in mainTemplate.json for changed files | `powershell-yaml` module, git |
| **Classic App Insights** | `validateClassicAppInsights.yaml` | Detects deprecated classic App Insights resources (Microsoft.Insights/components without WorkspaceResourceId) in newly added files | `powershell-yaml` module, git |
| **Hyperlink Validation** | `hyperlinkValidator.yaml` | Validates URLs in solution files — checks for 404s, 500s, broken links | `powershell-yaml` module, git, **network access** |
| **TruffleHog (Secrets)** | `ScanSecrets.yaml` | Scans for hardcoded secrets/credentials using verified-only detection | `trufflehog` CLI (external tool) |

**Important notes:**
- These validators check **committed changes** (`git diff HEAD^ HEAD`). Commit your changes before running for full coverage.
- **Hyperlink Validation** is slow — it makes HTTP requests with a 20-second timeout per URL. It requires network connectivity and will be skipped if the network is unavailable.
- **TruffleHog** is optional — it requires the `trufflehog` CLI to be installed ([install guide](https://github.com/trufflesecurity/trufflehog#installation)). If not installed, it is skipped with a message.
- The 3 PowerShell validators require the `powershell-yaml` module; the script auto-installs it if missing.

**Runtime detection:** The script checks which runtimes are installed:
- If **.NET Core 3.1** is available → runs Detection Schema (scoped) and Non-ASCII (full repo)
- If **.NET 8.0** is available → runs KQL validator (scoped to solution)
- If a required .NET runtime is **missing** → skips that validator with a message:
  ```
  ⏭  Detection Schema validation skipped — .NET Core 3.1 runtime not installed.
     Install it from: https://dotnet.microsoft.com/download/dotnet/3.1
  ```
- **ARM-TTK** uses the ARM-TTK PowerShell module to run `Test-AzTemplate` — the same checks as `.github/actions/entrypoint.ps1` with identical skips and `contentProductId`/`id` error filters. The module auto-clones from GitHub on first run (stored in `.arm-ttk/`, gitignored). If the `Package/` folder exists, ARM-TTK runs automatically.
- If the solution has **no relevant content files** (e.g., no Analytic Rules) → skips with:
  ```
  ⏭  Detection Schema validation skipped — no Analytic Rules found in <SolutionName>.
  ```

## Prerequisites

Before building, ensure:

1. **Node.js 16+** is installed
2. **npm dependencies** are installed: `npm install` (from repo root)
3. **TypeScript is compiled**: `npx tsc` (from repo root)
4. **PowerShell 7+** is installed (for the V3 packaging script)
5. **.NET Core 3.1 runtime** — required for Detection Schema and Non-ASCII validators ([download](https://dotnet.microsoft.com/download/dotnet/3.1))
6. **.NET 8.0 runtime** — required for KQL validator ([download](https://dotnet.microsoft.com/download/dotnet/8.0))
7. **Git** — required for ARM-TTK module auto-clone on first run and for Step 4 CI validators

> **Note:** Items 5 and 6 are optional. If the required .NET runtime is not installed, those validators will be skipped with a message. The remaining validators will still run.

8. **`powershell-yaml` module** — required for Step 4 CI PowerShell validators (auto-installed if missing)
9. **Network access** — required for Hyperlink Validation (skipped if unavailable)
10. **TruffleHog CLI** — optional, for secret scanning ([install](https://github.com/trufflesecurity/trufflehog#installation))

## Validation Only (Without Packaging)

To run just the validation checks:

```powershell
# Validate a specific solution
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection" -SkipPackaging

# Or run the validation script directly
node .script/local-validation/validate.js --path "Solutions/CrowdStrike Falcon Endpoint Protection"

# Validate with JSON output (for programmatic consumption)
node .script/local-validation/validate.js --path "Solutions/CrowdStrike Falcon Endpoint Protection" --json
```

## Sample User Commands

These are example prompts a user might type in their agent (GitHub Copilot, Cursor, Windsurf, etc.). For each, follow the workflow described above.

### Build / Package a Solution

| User Says | What You Do |
|-----------|-------------|
| *"Build V3 solution for CrowdStrike"* | Ask the user what changed (or check `git diff`), then run with `-SolutionName "CrowdStrike" -ReleaseNotes "<description>"`. If multiple matches, present the list and ask user to pick. |
| *"Package the Palo Alto solution"* | Run with `-SolutionName "Palo Alto"`. Multiple matches expected — present list, let user choose. Then ask what changed for release notes. |
| *"Build 1Password with a minor version bump"* | Ask what changed, then run with `-SolutionName "1Password" -VersionBump minor -ReleaseNotes "<description>"`. |
| *"Create a new package for Salesforce Service Cloud"* | Ask what changed, then run with `-SolutionName "Salesforce Service Cloud" -ReleaseNotes "<description>"`. |
| *"Rebuild the CrowdStrike solution — I added a new RTEM connector"* | User already described the change. Run with `-SolutionName "CrowdStrike" -ReleaseNotes "Added new RTEM data connector"`. |
| *"Package Cisco solution as a major release"* | Run with `-SolutionName "Cisco" -VersionBump major`. Multiple matches likely — ask user to pick AND describe changes. |

### Validate Only (No Packaging)

| User Says | What You Do |
|-----------|-------------|
| *"Validate the CrowdStrike solution"* | Run with `-SolutionName "CrowdStrike" -SkipPackaging`. |
| *"Run validations on Palo Alto Prisma Cloud CWPP"* | Run with `-SolutionName "Palo Alto Prisma Cloud CWPP" -SkipPackaging`. |
| *"Check if my solution passes CI checks"* | Ask which solution, then run with `-SkipPackaging`. |
| *"Validate all JSON files in the Fortinet solution"* | Run with `-SolutionName "Fortinet" -SkipPackaging`. |

### Package Only (No Validation)

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
2. **If your terminal timed out** or you only see partial output (no `[REPORT_END]`), **read the report file instead**: run `Get-Content .script/local-validation/last-report.md` from the repo root and display its contents. The script always saves the full report to this file.
3. **Do NOT respond with partial results.** If you don't see `[REPORT_END]` yet, the script is still running — wait for it.
4. Present the full report in your chat response — the text between `[REPORT_START]` and `[REPORT_END]`
5. Do NOT summarize, paraphrase, or abbreviate the report — show it in full
6. If a validator failed, add your own analysis and fix suggestions **after** the report block

**NEVER tell the user to "check the terminal." NEVER give partial step-by-step updates.**

The report includes:
- **Header** — solution name, version change, date, total duration
- **Step 1** — packaging result, package file path, version sync status, release notes status
- **Step 2** — per-validator pass/fail/skip counts with error details for failures
- **Step 3** — .NET validator results with test counts, durations, and scoping info
- **Step 4** — CI PowerShell validator results (field types, classic App Insights, hyperlinks, TruffleHog)
- **Summary** — overall pass/fail status with totals across all validators

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


