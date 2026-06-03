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

# Validate a specific connector
node .script/local-validation/validate.js --path DataConnectors/MyConnector
```

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
| `kql` | KQL Validation | — | — | KQL syntax and best practices (.NET, scoped to solution) |
| `detection-schema` | Detection Template Schema | — | — | Detection YAML structure (.NET, scoped to solution) |
| `non-ascii` | Non-ASCII | — | — | Non-ASCII character detection (.NET, entire repo) |
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
- **.NET SDK 6.0+** (optional — for KQL, Detection Schema, Non-ASCII validators; Detection Schema and KQL are scoped to the target solution for fast local runs)
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

### Import errors
Make sure TypeScript is compiled:
```bash
npm run tsc
```

## File Inventory (New Files Only)

This feature adds the following files — **no existing files are modified**:

```
.script/local-validation/
├── validate.ts    # Main validation runner (TypeScript source)
├── validate.js    # Compiled JavaScript (generated by tsc)
└── README.md      # This documentation
```
