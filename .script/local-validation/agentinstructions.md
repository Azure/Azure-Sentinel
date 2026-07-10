---
applyTo: "Solutions/**"
---

# Validation & Remediation Workflow — Agent Instructions

This file defines the end-to-end agent workflow for validating a Microsoft Sentinel solution, remediating any failures, and preparing it for a Pull Request. Follow every step in order. **Do not skip steps or ask the user to handle environment setup — the agent is responsible for all of it.**

---

## When to Use This Workflow

Run this workflow when a developer says any of the following:
- "Validate \[solution name\]"
- "Run validation on \[solution name\]"
- "Check if \[solution name\] passes CI"
- "Fix validation errors in \[solution name\]"
- "Get \[solution name\] ready for a PR"
- "Run local-validation against \[solution name\]"

---

## Step 1 — Identify the Solution

If the user has not provided a solution name, ask:

> Which solution would you like to validate? (Provide the folder name under `Solutions/`, or a partial name — fuzzy matching is supported.)

Once you have a name, proceed to Step 2.

---

## Step 2 — Check & Install Prerequisites

Before running validation, silently verify that all required tools are present and install any that are missing. **Do not ask the user to install anything — handle it automatically.**

### 2a — Node.js

```powershell
node --version
```

If `node` is not found:
1. Download and install the Node.js LTS installer silently:
   ```powershell
   $installer = "$env:TEMP\node-lts.msi"
   Invoke-WebRequest "https://nodejs.org/dist/latest-v20.x/node-v20.x.x-x64.msi" -OutFile $installer
   ```
   > Use the [Node.js releases index](https://nodejs.org/dist/index.json) to get the exact current LTS filename:
   > ```powershell
   > $lts = (Invoke-RestMethod "https://nodejs.org/dist/index.json") | Where-Object { $_.lts } | Select-Object -First 1
   > $msi = "https://nodejs.org/dist/$($lts.version)/node-$($lts.version)-x64.msi"
   > Invoke-WebRequest $msi -OutFile "$env:TEMP\node-lts.msi"
   > Start-Process msiexec.exe -ArgumentList "/i `"$env:TEMP\node-lts.msi`" /quiet /norestart" -Wait
   > ```
2. Refresh the PATH in the current shell:
   ```powershell
   $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
   ```
3. Verify: `node --version` — if it still fails, inform the user and stop.

### 2b — npm dependencies

```powershell
if (!(Test-Path "node_modules")) { npm install }
```

### 2c — Compile TypeScript

```powershell
if (!(Test-Path ".script\local-validation\validate.js")) { npx tsc }
```

### 2d — .NET SDK (optional but recommended)

```powershell
dotnet --list-sdks
```

If no SDK is found, install .NET 8.0 SDK silently:
```powershell
$dotnetInstall = "$env:TEMP\dotnet-install.ps1"
Invoke-WebRequest "https://dot.net/v1/dotnet-install.ps1" -OutFile $dotnetInstall
& $dotnetInstall -Channel 8.0 -InstallDir "$env:LOCALAPPDATA\Microsoft\dotnet"
$env:PATH += ";$env:LOCALAPPDATA\Microsoft\dotnet"
```

### 2e — TruffleHog (optional)

```powershell
Get-Command trufflehog -ErrorAction SilentlyContinue
```

If not found, install via winget (silently, no prompts):
```powershell
winget install trufflesecurity.trufflehog --silent --accept-package-agreements --accept-source-agreements
```

If winget is not available, skip TruffleHog — it is optional.

---

## Step 3 — Run Validation

Tell the user **before** running:

> 🔄 Running full validation for **{SolutionName}**. This typically takes **3–10 minutes** — it runs 21 validators including .NET tests, ARM-TTK, and hyperlink checks. I'll present the complete report when it finishes.

Then run the following from the **repository root**:

```powershell
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "{SolutionName}" -SkipPackaging
```

> **Note:** Use `-SkipPackaging` for validation-only runs. If the user also wants to rebuild the solution package, ask them what type of version bump this is (`patch` / `minor` / `major`) and what changed (for release notes), then run without `-SkipPackaging`. See `packaging.instructions.md` for the full packaging workflow.

### Handling Multiple Solution Matches (exit code 2)

If the script exits with code 2 and prints a numbered list of matching solutions:
1. Present the list to the user exactly as printed
2. Ask: "I found multiple matches — which solution did you mean?"
3. Wait for the user's selection, then re-run with the exact folder name

---

## Step 4 — Display the Full Report

After the script finishes:

1. Show the **complete report** — the text between `[REPORT_START]` and `[REPORT_END]`
2. If those markers are not present (e.g., terminal timed out), retrieve the saved report instead:
   ```powershell
   Get-Content .script/local-validation/last-report.md
   ```
3. Display it in full — **do not summarize, paraphrase, or abbreviate**

---

## Step 5 — Evaluate Results

After displaying the report, assess the outcome:

### If validators show SKIP due to missing tools → go back to Step 2

Re-check prerequisites. A validator showing SKIP means a tool is still missing — install it and re-run.

### If all validators passed (or only SKIP with no FAIL) → skip to Step 8

### If failures exist → continue to Step 6

---

## Step 6 — Plan Remediation

For each failed validator:
1. Identify the validator name and the file(s) affected
2. Read the affected file(s) to understand the current state
3. Determine exactly what change is needed based on the error message

Compile all planned fixes and present them to the user as a clear numbered list:

> Here's what I found and what I plan to fix:
>
> 1. **\[Validator\]** — `Solutions/MyApp/Data/connector.json`: \<describe the problem and the planned fix\>
> 2. **\[Validator\]** — `Solutions/MyApp/Analytic Rules/rule.yaml`: \<describe the problem and the planned fix\>
> 3. ...

Reference the table below for common failure patterns and their fixes.

---

## Step 7 — Confirm & Apply Fixes

Ask the user:

> Shall I go ahead and apply these fixes?

**Wait for explicit confirmation before editing any file.**

Once confirmed:
1. Apply each fix carefully — read the file before editing
2. Do not make changes beyond what is listed in the plan
3. After all fixes are applied, go back to **Step 3** and re-run validation
4. Repeat Steps 4–7 until zero validation failures remain

---

## Step 8 — Zero Errors: Prompt for PR

When the report shows all validators passed:

> ✅ All validation checks passed for **{SolutionName}**!
>
> Your solution is ready for submission. Please open a Pull Request targeting the `main` branch and include the Content Engineering label so it gets routed for review.
>
> Suggested PR title: `[Solution] {SolutionName} — {brief description of changes}`

Do **not** open or submit the PR automatically. This is always a manual action by the developer.

---

## Common Failures & Fixes

| Validator | Typical Error | Fix |
|-----------|---------------|-----|
| **Content Branding** | `"Azure Sentinel"` found in file | Replace all occurrences of `"Azure Sentinel"` with `"Microsoft Sentinel"` |
| **JSON Syntax** | `Unexpected token` or `Unexpected end` | Fix malformed JSON — missing comma, bracket, or quote |
| **YAML Syntax** | `Bad indentation` or `Duplicate key` | Fix YAML indentation or remove duplicate keys |
| **Data Connector Schema** | `Missing required field` | Add the required field per the data connector schema |
| **Solution Validation** | `Missing domains/verticals` | Add valid `Domains` and `Verticals` to `Solution_*.json` |
| **ID Change Detection** | `Template ID changed` | Revert the `id`/`templateSpecId` field to its original value — IDs must never change |
| **Playbook Validation** | `Missing metadata field` | Add the missing field to the ARM template `metadata` block |
| **Workbook Template** | `Schema URI mismatch` | Correct the `$schema` field to match the expected workbook schema URI |
| **Logo** | `File exceeds 5KB` or `Not SVG format` | Replace with a valid SVG file ≤5KB |
| **Sample Data** | `Unsanitized email` | Replace email addresses with `sanitized@sanitized.com` |
| **ARM-TTK** | Various template violations | Address each flagged template issue; do not hand-edit `Package/` files — re-run packaging instead |
| **Detection Schema** | `Missing required field` or `Invalid entity mapping` | Fix the analytic rule YAML to match the detection schema requirements |
| **KQL** | `Syntax error` in query | Correct the KQL syntax in the affected detection, hunting query, or parser |
| **Non-ASCII** | `Non-ASCII character at line X` | Remove or replace the non-ASCII character in the YAML file |
| **Hyperlink Validation** | `404` or broken URL | Update or remove the broken URL |
| **TruffleHog** | `Potential secret detected` | Remove the hardcoded credential; use a parameter or environment variable instead |

---

## Important Rules

- **Always show the full report.** Never summarize or skip sections.
- **Always confirm changes with the user** before editing files.
- **Never hand-edit `Package/` folder files** — they are auto-generated by the packaging script.
- **Always re-run validation** after making changes — never assume a fix worked without re-validating.
- **Never submit PRs automatically** — always prompt the user and let them do it.
- **Do not modify files** in `.script/utils/`, `.script/tests/`, or `.github/workflows/`.
- **If a fix is unclear**, ask the user how they want to resolve it rather than guessing.
