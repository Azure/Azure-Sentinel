# Validation Flow Guide (Offline / CI & Authoring Validation)

This guide explains how to run the **Validation Flow** for Microsoft Sentinel and Defender XDR solution pull requests using the Solution Manager toolkit (`Tools/SentinelToXDRMigration`).

For the formal machine-readable check definitions, see:
- [Validation Checklist Specification (`validation-checks.md`)](qualification/validation-checks.md)
- [Migration Overlay Checklist (`migration-checks.md`)](qualification/migration-checks.md)
- [PR Qualification Checklists Overview (`qualification/README.md`)](qualification/README.md)

---

## No-Code / Chat-Based Experience (LLM Agent Orchestration)

**You do not need to write code or memorize CLI flags to run this flow.** The entire Validation experience can be driven conversationally in chat using LLM coding agents (GitHub Copilot CLI, VS Code Copilot Chat, or Claude Code) via the repository's built-in **`XDR Solution Manager`** agent (`.github/agents/xdr-solution-manager.agent.md`) and skills (`sentinel-xdr-end-to-end-orchestrator`, `sentinel-xdr-migration`):

- **How it works:** Simply prompt the agent in plain English—the agent automatically invokes the deterministic Python and PowerShell toolkit commands below, manages `workflow-state.json` and run IDs, presents structured batch review forms (`ask_user`) for any mapping assumptions or exclusions, runs V3.1 packaging and `build-and-validate.ps1`, and generates the final HTML/Markdown `Evidence/` reports.
- **Example Chat Prompts:**
  - *"Validate the `Solutions/<SolutionName>` solution using the Validation flow and generate the qualification report."*
  - *"Migrate `Solutions/<SolutionName>` to Defender XDR in Authoring mode, validate all rules and workbooks, package v3.2.2, and run PR validation checks."*
  - *"Resume the Validation flow for `Solutions/<SolutionName>` and apply waivers for static KQL false positives."*

For contributors or CI pipelines that prefer invoking the deterministic CLI directly, follow the step-by-step commands in Section 3.

---

## 1. Purpose and Execution Boundary

The **Validation Flow** verifies offline authoring contracts, structural YAML/JSON validity, dependency provenance, mock fixture existence and schema validity, V3.1 hybrid package integrity, and repository CI validators—**without performing any cloud writes or requiring live lab ingestion**.

| Attribute | Contract |
| :--- | :--- |
| **Workflow Profile** | `authoring` (default) |
| **Evaluation Mode** | `--mode validation` (combines `validation-checks.md` + static `category: validation` checks from `migration-checks.md` when `--is-migration` is active) |
| **Cloud Writes** | **None.** No lab deployments, DCR creation, mock ingestion, or rule enablement. |
| **Rollup Outcomes** | `Validated` (100% pass, no waivers/exclusions) or `Partially Validated` (all safety gates pass; $\ge 1$ valid author exception or acknowledged inventory exclusion) |
| **PR Labels** | `Validation` (plus `Migration` when migrating Sentinel content to `XDR Detections/` or `XDR Workbooks/`) |

---

## 2. Prerequisites

1. **Python 3.11 or 3.12** with the toolkit installed in editable mode:
   ```powershell
   python -m pip install -e Tools/SentinelToXDRMigration
   ```
2. **PowerShell 7 (`pwsh`)** for running V3.1 packaging and the official local validation suite (`.script/local-validation/build-and-validate.ps1`).
3. **Solution Version $\ge 3.2.2$ and $< 4.0.0$:** All toolkit-validated V3.1 solutions must target version `3.2.2` or higher (`< 4.0.0`).

---

## 3. Step-by-Step Validation Flow

### Step 1 — Initialize or Resume the Authoring Workflow

Check existing workflow runs first. If none exist, initialize an `authoring` run with a target version $\ge 3.2.2$:

```powershell
# Check existing runs
sentinel-xdr-migration workflow-runs --solution "Solutions/<SolutionName>"
sentinel-xdr-migration workflow-status --solution "Solutions/<SolutionName>"

# Initialize a new authoring run targeting 3.2.2 (or use --version-bump patch/minor/major)
sentinel-xdr-migration workflow-init `
  --solution "Solutions/<SolutionName>" `
  --workflow-profile authoring `
  --version-bump none `
  --target-version 3.2.2 `
  --arm-validation-method arm-ttk
```

> **Note:** Record the returned `<run-id>`. Pass `--run-id "<run-id>"` to all subsequent commands. State and artifacts are stored in `Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/` (Git-ignored).

### Step 2 — Discovery & Inventory (`E2E-V01`, `TK-V01`)

Inspect the solution to inventory all recursive source content (Analytic Rules, Workbooks, Hunting Queries, Parsers, Data Connectors, Playbooks) and existing XDR artifacts:

```powershell
sentinel-xdr-migration inspect `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"
```

- Every logical content item in the solution must either be packaged or have an explicit author exclusion recorded (`E2E-V01`).
- Duplicate GUIDs or ambiguous source-to-target pairings block validation (`TK-V01`).

### Step 3 — Content Conversion & Dependency Provenance (`TK-V02`..`TK-V09`)

If the PR migrates Sentinel Analytic Rules or Workbooks to Defender XDR (see [Migration Flow Guide](migration-flow-readme.md)):

```powershell
# Convert Sentinel Analytic Rules -> XDR Detections/ and Workbooks -> XDR Workbooks/
sentinel-xdr-migration convert `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

# Plan and verify requiredWorkloads and requiredDataConnectors provenance
sentinel-xdr-migration dependency-plan `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

# For solutions with XDR Workbooks: verify workbook dependencies and clean public JSON
sentinel-xdr-migration workbook-dependencies `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"
sentinel-xdr-migration workbook-publication-clean `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"
```

### Step 4 — Structural & Offline Content Validation (`VAL-RULE-01`, `VAL-WB-01`, `VAL-PARSER-01`, `VAL-DC-01`)

Run structural validation on the solution content and generated XDR artifacts:

```powershell
sentinel-xdr-migration validate `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"
```

For offline Authoring without live query execution, complete the workflow validation stage in `offline-authoring` mode (`runtimeStatus=not-run`), which discloses in the report that live KQL queries were not executed against a workspace/tenant.

*(Optional)* If you have read-only access to a Defender XDR tenant and want to validate converted Advanced Hunting queries during Authoring without switching to full Qualification:
```powershell
sentinel-xdr-migration plan-runtime-query-consent --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration review-runtime-query-consent --solution "Solutions/<SolutionName>" --run-id "<run-id>" --approve-family defenderXdrQueryFamily
sentinel-xdr-migration validate-advanced-hunting --solution "Solutions/<SolutionName>" --run-id "<run-id>"
```

### Step 5 — Mock Data Existence & Schema Validation (`E2E-V02`, `E2E-V03`, `VAL-SAMPLE-01`)

Validation requires schema-valid JSON mock fixtures for **all packaged** detections and workbooks:
- **`E2E-V02` (Detections):** Every packaged Sentinel Analytic Rule and Defender XDR Custom Detection must map to an existing, non-empty, schema-valid JSON mock file (converted AR/CD pairs share one `mock.json` scenario).
- **`E2E-V03` (Workbooks):** Every packaged Sentinel or Defender Workbook must map to schema-valid JSON mock fixtures covering its query tables.
- **`TK-G07` (Privacy & Sanitization):** Mock fixtures and sample data must contain only synthetic/sanitized values (no live customer PII, credentials, or tenant secrets).

### Step 6 — V3.1 Hybrid Solution Packaging (`VAL-PKG-01`, `VAL-PKG-02`, `TK-V10`..`TK-V13`)

Build the V3.1 hybrid package (`Package/mainTemplate.json`, `Package/createUiDefinition.json`, and `Package/<version>.zip`):

```powershell
# If inputs changed after initialization, plan the release action against the current input hash
sentinel-xdr-migration workflow-plan-package-release `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>" `
  --target-version 3.2.2 `
  --expected-package-input-sha256 "<current-package-input-sha256>"

# Run V3.1 packager
sentinel-xdr-migration package-v3-1 `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>" `
  --version-bump none `
  --target-version 3.2.2
```

> **Important:** Always use `package-v3-1`. Never use the legacy V3 or V4 packagers for solutions containing `XDR Detections/` or `XDR Workbooks/`.

### Step 7 — Official Repository Build & Validation Suite (`VAL-CI-01`)

Run the repository's official local validation script bound to the V3.1 package receipt:

```powershell
pwsh .script/local-validation/build-and-validate.ps1 `
  -SolutionName "<SolutionName>" `
  -ContentRoot "." `
  -SkipPackaging `
  -PackageReportPath "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/packaging.v3_1.json" `
  -VersionBump none `
  -ValidationSkip ""
```

This verifies:
- `SolutionValidator` (`SolutionMetadata.json`, `Data/Solution_*.json`, `ReleaseNotes.md` in `DD-MM-YYYY` format)
- `DetectionsYamlValidation` & `KqlValidations`
- `WorkbooksValidation` & `PlaybooksValidation`
- `DocumentsLinkValidation` (no locale segments like `/en-us/` in `learn.microsoft.com`, `docs.microsoft.com`, or `azure.microsoft.com` URLs)
- `ARM-TTK` template validation on `Package/mainTemplate.json` and `Package/createUiDefinition.json`

### Step 8 — Evaluate the Validation Checklist & Generate `Evidence/` Reports

Run `pr-qualify` in `validation` mode to evaluate all applicable checks in `validation-checks.md` (and `migration-checks.md` when migrating) and generate the reviewer-facing HTML, Markdown, and JSON artifacts:

```powershell
sentinel-xdr-migration pr-qualify `
  --solution "Solutions/<SolutionName>" `
  --mode validation `
  --is-migration
```

*(Omit `--is-migration` or pass `--no-migration` for general non-migration solution PRs.)*

#### Supplying Author Waivers or Acknowledged Exclusions (`Partially Validated`)

If a non-safety check fails or is skipped due to an upstream limitation (for example, a static KQL analyzer limitation or an unmigrated legacy rule), pass structured JSON files:

```powershell
sentinel-xdr-migration pr-qualify `
  --solution "Solutions/<SolutionName>" `
  --mode validation `
  --is-migration `
  --waivers-file "Solutions/<SolutionName>/Evidence/waivers.json" `
  --acknowledged-exclusions-file "Solutions/<SolutionName>/Evidence/exclusions.json"
```

- **Waivers format (`--waivers-file`):**
  ```json
  {
    "VAL-CI-01": {
      "authorJustification": "Static analyzer does not yet register Advanced Hunting AlertEvidence table.",
      "supportingEvidenceRef": "Evidence/qualification-evidence.json",
      "knownLimitationCategory": "kql-static-analyzer-schema-gap"
    }
  }
  ```
- **Non-waivable safety gates:** `TK-G02`, `TK-G03`, `TK-G04`, `TK-G06`, `TK-G07`, `E2E-G01`, and `TK-Q11` can never be waived.

---

## 4. Generated Artifacts and Rollup Outcomes

`pr-qualify` writes the following trackable files (default output directory: `Solutions/<SolutionName>/Evidence/pr-qualification/` or `Solutions/<SolutionName>/Evidence/`):

| Artifact | Purpose |
| :--- | :--- |
| `qualification-report.html` | Interactive HTML dashboard showing rollup status, check counts, observed values, and clickable links to evidence receipts |
| `qualification-summary.md` | Markdown summary suitable for embedding or linking in the GitHub PR description |
| `qualification-evidence.json` | Machine-readable check evaluation receipt bound to input/head SHA-256 hashes |

| Rollup Outcome | Criteria |
| :--- | :--- |
| **`Validated`** | All applicable checks in `validation-checks.md` (plus static `migration-checks.md` checks if active) are `PASS`, with 100% packaged inventory and zero waivers/exclusions. |
| **`Partially Validated`** | All non-waivable safety gates pass, zero unresolved `FAIL`/`SKIPPED`/`BLOCKED` checks remain, and $\ge 1$ check is `WAIVED_WITH_AUTHOR_EVIDENCE` or has an acknowledged inventory exclusion in `E2E-V01`. |
