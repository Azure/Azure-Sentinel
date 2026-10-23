# Local Validation Runner

Run the same CI validation checks that GitHub Actions performs — **locally**, without GitHub API access, PR context, or secrets.

## Quick Start

```bash
# From the repository root:
cd /path/to/AzureSentinel

# Install dependencies (if not already done)
npm install

# Compile TypeScript (if not already done)
npm run tsc

# Run validations on your changed files (auto-detects branch)
node .script/local-validation/validate.js
```

That's it. The tool auto-detects your current branch, diffs against `main` (or `master`), and runs all applicable validators.

## Usage

### Validate Changed Files (Default)

```bash
# Auto-detect: diff current branch against main/master
node .script/local-validation/validate.js

# Explicit target branch
node .script/local-validation/validate.js --diff main
node .script/local-validation/validate.js --diff feature/base-branch
```

### Validate All Files in a Directory

```bash
# Validate everything under a solution folder
node .script/local-validation/validate.js --path Solutions/MySolution

# Same checks against a different content checkout; helper code still loads from this checkout
node .script/local-validation/validate.js \
  --repository-root /path/to/content-checkout \
  --path Solutions/MySolution \
  --only json,yaml \
  --json-file .script/local-validation/Logs/results.json

# Validate a specific connector
node .script/local-validation/validate.js --path DataConnectors/MyConnector
```

The validator and .NET test projects still load from the toolkit checkout. When standalone `--files`, `--diff`, or auto-discovery runs a .NET validator, `--repository-root` is passed to its content loaders through `SENTINEL_VALIDATION_CONTENT_ROOT`; standalone `--path` continues to skip repo-wide .NET tests.

### Validate Specific Files

```bash
node .script/local-validation/validate.js --files Solutions/MySolution/data.json DataConnectors/connector.json
```

### Filter Validators

```bash
# Run only JSON and YAML syntax checks
node .script/local-validation/validate.js --only json,yaml

# Skip slow .NET validators
node .script/local-validation/validate.js --skip kql,detection-schema,non-ascii

# Run only data connector validation
node .script/local-validation/validate.js --only data-connector
```

### Output Options

```bash
# Verbose output (show all files, not just failures)
node .script/local-validation/validate.js --verbose

# JSON output (for programmatic consumption by agents/scripts)
node .script/local-validation/validate.js --json

# Combine: JSON output for a specific path
node .script/local-validation/validate.js --path Solutions/MySolution --json
```

## Available Validators

| ID | Name | File Types | Paths | What It Checks |
|----|------|-----------|-------|----------------|
| `json` | JSON Syntax | `.json` | All | Valid JSON parsing |
| `yaml` | YAML Syntax | `.yaml`, `.yml` | All | Valid YAML parsing |
| `data-connector` | Data Connector | `.json` | `DataConnectors/`, `Solutions/` | Schema validation, ID, data types, permissions |
| `content` | Content (MS Branding) | `.json` | Data/DataConnectors | "Azure Sentinel" → "Microsoft Sentinel" text |
| `logo` | Logo | All | `Logos/`, `Solutions/`, `Workbooks/Images/` | SVG format, ≤5KB, valid SVG content |
| `sample-data` | Sample Data | `.json` | `Sample Data/` | Email sanitization, array format |
| `playbook` | Playbook | `.json` | `Playbooks/`, `Solutions/` | ARM template schema, playbook resources |
| `workbook-template` | Workbook Template | `.json` | `Workbooks/`, `Solutions/` | Schema URI, version, template ID |
| `workbook-metadata` | Workbook Metadata | `WorkbooksMetadata.json` | `Workbooks/` | Schema, unique keys, images, version increment |
| `documents-link` | Documents Link | All | All | No locale codes in documentation URLs |
| `solution` | Solution | `.json` | `Solutions/` | Domains/verticals, support, branding, ID |
| `id-change` | ID Change | `.yaml`, `.yml`, `.json` | `Detections/`, `Solutions/` | Template IDs must not change |
| `xdr-detection` | XDR Detection | `.yaml`, `.yml`, `.json` | `Solutions/<Solution>/XDR Detections/`, `Data/`, `Package/` | `xdr-detection.schema.json`, `contentProvenance`, `requiredWorkloads`, `requiredDataConnectors`, source rule SHA-256 freshness, `Data/*.json` selection, and packaged `CustomDetection` resources |
| `xdr-workbook` | XDR Workbook | `.json` | `Solutions/<Solution>/XDR Workbooks/`, `Data/`, `Package/` | `xdr-workbook.schema.json`, `contentProvenance`, `requiredWorkloads`, `requiredDataConnectors`, `requiredWorkspaceFunctions`, query contracts, and packaged `DefenderWorkbook-*` resource & `dependsOn` integrity |
| `kql` | KQL Validation | — | — | KQL syntax and best practices (.NET, scoped to solution) |
| `detection-schema` | Detection Template Schema | — | — | Detection YAML structure (.NET, scoped to solution) |
| `non-ascii` | Non-ASCII | — | — | Non-ASCII character detection (.NET; scoped by the build runner) |
| `arm-ttk` | ARM-TTK | `.json` | `Solutions/` | ARM template testing (Docker — same as GitHub CI) |

## How It Works

### Architecture

The GitHub CI pipeline uses this flow:
```
GitHub Actions → gitHubWrapper.ts (Octokit API) → changedFilesValidator.ts → individual validators
```

This local runner replaces the GitHub-dependent layers:
```
CLI args → local git diff (or glob) → same checker utilities → local report
```

The **validation logic is identical** — this tool imports the same pure checker functions
(`jsonSchemaChecker`, `idChecker`, `dataTypeChecker`, `permissionsChecker`, etc.) that the CI pipeline uses.
The only difference is how files are discovered (local git vs GitHub API).

### CI / Local Sync Strategy

The local validation pipeline is designed to stay in sync with CI by **sharing code at every layer possible**:

| Layer | Shared? | Details |
|-------|---------|---------|
| **TypeScript validators** (Step 2) | **Yes — same code** | `validate.js` imports the same checker functions from `.script/utils/` that CI uses. No duplication. |
| **.NET validators** (Step 3) | **Yes — same test projects** | Both CI and local run `dotnet test` against the same `.csproj` files. No duplication. |
| **PowerShell validators** (Step 4) | **Yes — same scripts** | `build-and-validate.ps1` calls the same `.script/package-automation/*.ps1` scripts that CI workflows invoke. |
| **ARM-TTK** (Step 3) | **Yes — same module + skips** | Local uses the same `Test-AzTemplate` invocation with identical skip lists as `.github/actions/entrypoint.ps1`. |
| **File discovery** | **No — by design** | CI uses GitHub API (`octokit.pulls.listFiles`); local uses `git diff` or glob. This is the only intentional divergence. |
| **Workflow config** (trigger paths, env vars) | **No — CI-only concern** | CI workflow YAML files contain trigger paths and environment variables that don't apply locally. |

**When adding a new validator:** Add the validation logic in a shared location (`.script/utils/` for TypeScript, `.script/package-automation/` for PowerShell, or a `.csproj` for .NET), then wire it into both the CI workflow and `build-and-validate.ps1`. This keeps the two in sync automatically.

### What's Different from CI

| Aspect | GitHub CI | Local Runner |
|--------|----------|--------------|
| File discovery | GitHub API (`octokit.pulls.listFiles`) | `git diff --name-status` |
| Authentication | GitHub App private keys | None needed |
| PR context | PR number, base/head branches | Local branch comparison |
| Result reporting | PR comments via Octokit | Console output / JSON |
| Version increment check | GitHub API + simple-git | Local git diff |
| .NET validators | GitHub-hosted runner | Local `dotnet test` |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All validations passed |
| `1` | One or more validations failed |
| `2` | Configuration or usage error |

## Requirements

- **Node.js 16+** with npm dependencies installed (`npm install`)
- **TypeScript compiled** (`npm run tsc`)
- **Git** (for `--diff` mode file discovery)
- **.NET SDK 6.0+** (optional — the build runner scopes KQL, Detection Schema, and Non-ASCII checks; standalone `--path` mode skips these repo-wide test projects)
- **Docker** (optional — for ARM-TTK validator, uses the same Dockerfile as GitHub CI)

## Integration with AI Agents

This tool is designed to be used by **any** agentic environment. For agent integration:

### For AI coding agents (Copilot, Cursor, Windsurf, etc.)

After making changes, run:
```bash
node .script/local-validation/validate.js --json
```

The `--json` flag outputs structured results that any agent can parse:
```json
{
  "summary": {
    "total": 15,
    "passed": 12,
    "failed": 2,
    "skipped": 1
  },
  "results": [
    {
      "validator": "JSON Syntax",
      "filePath": "Solutions/MySolution/data.json",
      "passed": true
    },
    {
      "validator": "Data Connector",
      "filePath": "DataConnectors/MyConnector/connector.json",
      "passed": false,
      "error": "Schema validation failed: missing required field 'permissions'"
    }
  ]
}
```

### For CI/CD integration

```bash
# In a pre-commit hook or local CI script
node .script/local-validation/validate.js --diff main
exit_code=$?
if [ $exit_code -ne 0 ]; then
  echo "Validation failed. Please fix errors before pushing."
  exit 1
fi
```

## Troubleshooting

### "Please run this script from the Azure Sentinel repository root directory"
Make sure you `cd` to the repo root before running the script.

### "Could not find or fetch branch 'main'"
Your repo might use `master` instead of `main`. Try:
```bash
node .script/local-validation/validate.js --diff master
```

### ".NET SDK not found"
The .NET validators (KQL, Detection Schema, Non-ASCII) require .NET SDK. Install it or skip them:
```bash
node .script/local-validation/validate.js --skip kql,detection-schema,non-ascii
```

The standalone `validate.js --path` command skips .NET validators because it cannot safely scope the repo-wide test projects. Use `build-and-validate.ps1 -SolutionName ... -SkipPackaging` for solution-scoped .NET checks.

With an explicit solution folder, validation examines current files in that folder, including uncommitted and untracked files; deleted files are excluded. The folder must be an existing direct child of `Solutions/`. The repo-history TruffleHog check is reported as skipped because it cannot be limited to one solution.
Solution-scoped hyperlink validation also excludes descendant path components named
`Logs`, `Reports`, or `Evidence` (case-insensitive, whole path segments), consistent
with the local TypeScript solution scan. Other names and path substrings remain in scope.

### Cross-Checkout Build Runner

`build-and-validate.ps1` derives its toolkit root from the script location. By default,
the content root is that same checkout, preserving the normal same-worktree behavior.
For selected content from another checkout, use `-ContentRoot <canonical-git-root>`
with `-SkipPackaging` and the official runner; packaging is rejected when roots differ.
The selected solution must be a non-symlink direct child of that content root's
`Solutions/`. TypeScript and .NET helper projects, PowerShell validation scripts,
configuration, and ARM-TTK dependencies remain in the toolkit root, while current
solution files and scoped .NET/PowerShell validation use the selected content root.

For post-V3.1 ARM deployment acceptance, run the existing validation checks in
validation-only mode and provide the exact V3.1 package report for the selected
workflow run:

```powershell
pwsh .script/local-validation/build-and-validate.ps1 `
  -SolutionName "MySolution" `
  -ContentRoot /path/to/content-checkout `
  -SkipPackaging `
  -PackageReportPath "Logs/sentinel-xdr-migration/<run-id>/packaging.v3_1.json" `
  -VersionBump none `
  -ValidationSkip ""
```

`-PackageReportPath` is optional for ordinary use. When supplied, the runner
requires `-SkipPackaging` and active validation, verifies that the V3.1 report
and its referenced artifacts are current, checks the report's package-input
fingerprint against current solution inputs before validation, and records the
package report's workflow/attempt IDs and exact artifact hashes. It fingerprints
all package inputs and every file in `Package/` before and after the existing
validation steps; changed content, package bytes, package report, `ContentRoot`,
or runner scripts makes the binding fail. The ignored evidence run contains
`build-and-validate-binding.json`, and the human-readable report contains its
path and SHA-256. The acceptance planner independently checks those emitted
fingerprints against current V3.1 package state and current files; it does not
infer validated hashes from the files' current state or use report timestamps.
This adds no validator and does not turn skipped checks into passes.

V3.1 package-input identities use Python `Path` ordering, which is
case-sensitive on POSIX and case-insensitive on Windows. The producer computes
both component-wise orderings and records only the semantics whose full file
fingerprint matches the package report's own `packageInputs.after.sha256`;
it also records the validation runner's platform. A cross-host validation run
therefore follows the packager identity rather than the runner's local sort.
Windows ordering lowercases each path component before ordinal component
comparison, matching `PureWindowsPath` rather than .NET's
`OrdinalIgnoreCase` string ordering.
If neither ordering matches, or Windows-equivalent paths make ordering
ambiguous, evidence capture fails closed. The independent `Package/` file
inventory retains its existing ordinal, case-sensitive path ordering.

The runner accepts `-EvidenceDirectory` only under the toolkit's ignored
`.script/local-validation/Logs/` folder. It creates a unique run subdirectory with the
complete TypeScript results JSON, separate TypeScript stdout/stderr logs, compile
output, complete captured output for invoked .NET/PowerShell/ARM-TTK helpers, and the
full report. The JSON file avoids console/native-process output truncation; a missing
or malformed report is a runner failure. A .NET invocation that exits without a test
summary or executed tests is reported as skipped, not passed. Skipped checks are counted
as skipped, not passed. Validation-only runs do not update solution data, release notes,
or packages.

For example:

```powershell
pwsh /path/to/toolkit/.script/local-validation/build-and-validate.ps1 `
  -SolutionName "MySolution" `
  -ContentRoot /path/to/content-checkout `
  -SkipPackaging `
  -VersionBump none `
  -ValidationSkip "" `
  -EvidenceDirectory ".script/local-validation/Logs/my-run"
```

### Import errors
Make sure TypeScript is compiled:
```bash
npm run tsc
```

## Build Outputs

`validate.js`, `validate.js.map`, `validate.d.ts`, and `validate.d.ts.map` are generated from `validate.ts` by `npm run tsc`.
