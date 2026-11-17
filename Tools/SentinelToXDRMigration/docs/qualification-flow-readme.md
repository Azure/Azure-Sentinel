# Qualification Flow Guide (Live Non-Production Lab Qualification)

This guide explains how to run the end-to-end **Qualification Flow** for Microsoft Sentinel and Defender XDR solution pull requests using the Solution Manager toolkit (`Tools/SentinelToXDRMigration`).

For the formal machine-readable check definitions, see:
- [Qualification Checklist Specification (`qualification-checks.md`)](qualification/qualification-checks.md)
- [Validation Checklist Specification (`validation-checks.md`)](qualification/validation-checks.md)
- [Migration Overlay Checklist (`migration-checks.md`)](qualification/migration-checks.md)
- [Canonical Agent Workflow (`end-to-end-migration.md`)](../agent-workflows/end-to-end-migration.md)

---

## No-Code / Chat-Based Experience (LLM Agent Orchestration)

**You do not need to write code or run CLI commands manually to qualify a solution.** The entire end-to-end Qualification experience is designed to be run conversationally in chat using LLM agents (GitHub Copilot CLI, VS Code Copilot Chat, or Claude Code) through the **`XDR Solution Manager`** agent (`.github/agents/xdr-solution-manager.agent.md`) and specialist skills (`sentinel-xdr-end-to-end-orchestrator`, `sentinel-solution-optional-testing`, `sentinel-xdr-alert-parity-validator`):

- **How it works:** Tell the agent which solution you want to qualify in your non-production lab. The agent inspects your `Solutions/<SolutionName>/.env` target, prompts you with structured approval dialogs before any read or write gate (`TK-G02`, `TK-G03`), executes live Log Analytics and Advanced Hunting KQL queries, deploys disabled rules/workbooks, generates and ingests shared `mock.json` telemetry via DCR, runs controlled alert parity (automatically restoring rules to `enabled: false`), runs Playwright workbook UI checks, and produces the sanitized `Evidence/qualification-report.html` and `Evidence/qualification-evidence.json` bundle.
- **Example Chat Prompts:**
  - *"Run full live Qualification on `Solutions/<SolutionName>` using the configured lab in `.env`."*
  - *"Qualify `Solutions/<SolutionName>`: deploy disabled rules, ingest mock data, run alert parity, and generate the HTML qualification report."*
  - *"Resume Qualification for `Solutions/<SolutionName>` from the Mock Ingestion stage."*

For operators who want to inspect or run the underlying deterministic CLI commands directly, see Section 4 below.

---

## 1. Purpose and Execution Boundary

The **Qualification Flow** extends the offline [Validation Flow](validation-flow-readme.md) with live, real-provider verification in an approved **non-production** Microsoft Sentinel and Defender XDR lab environment:

```text
Discovery -> Conversion -> Validation -> Packaging -> Deployment -> Mock Ingestion -> Alert Parity -> Portal/UI QA -> Report
```

| Attribute | Contract |
| :--- | :--- |
| **Workflow Profile** | `qualification` (explicit opt-in required; never inferred from `.env`) |
| **Evaluation Mode** | `--mode full` (or `--mode qualification`) |
| **Prerequisite (`QUAL-00`)** | Upstream Validation checklist rollup must be `Validated` or `Partially Validated` |
| **Real Providers (`E2E-G01`)** | Mandatory real Azure ARM, Log Analytics, Microsoft Graph Advanced Hunting/Custom Detection, Logs Ingestion API, and Playwright/portal evidence. Dry-run or simulated fallbacks are rejected. |
| **Rollup Outcomes** | `Qualified` (all applicable Validation + Qualification checks `PASS`, zero waivers/exclusions) or `Conditionally Qualified` (`QUAL-00` and all safety gates pass; $\ge 1$ valid author exception or `Partially Validated` upstream) |
| **PR Labels** | `Qualification` (plus `Migration` when migrating Sentinel content to `XDR Detections/` or `XDR Workbooks/`) |

---

## 2. Prerequisites & Lab Setup

1. **Non-Production Lab Environment:**
   - Dedicated test Microsoft Entra tenant with **Microsoft Defender XDR** ([Set up your Microsoft Defender XDR trial in a lab environment](https://learn.microsoft.com/defender-xdr/setup-m365deval))
   - Non-production **Microsoft Sentinel** Log Analytics workspace onboarded to Defender XDR ([Microsoft Sentinel 31-day free trial](https://learn.microsoft.com/azure/sentinel/billing#free-trial))
2. **Required Identity & Permissions (`TK-G03`, `TK-G04`):**
   - **Azure CLI (`az login`):** Authenticated to the target tenant and subscription with permissions to read/deploy Sentinel resources, DCRs/DCEs, and custom tables in the target resource group.
   - **Microsoft Graph Delegated Scopes:** `ThreatHunting.Read.All` (Advanced Hunting query execution) and `CustomDetection.ReadWrite.All` (deploying disabled Custom Detections and controlled alert parity).
   - *Tip:* If Graph scopes are missing on your lab app registration, use `Tools/SentinelToXDRMigration/solution_manager/qualification/templates/grant-graph-hunting-scopes.arm.json` after explicit approval.
3. **Solution-Local `.env` Configuration:**
   Copy `Tools/SentinelToXDRMigration/.env.example` to `Solutions/<SolutionName>/.env` (Git-ignored) and set the two literal identifiers:
   ```dotenv
   AZURE_TENANT_ID=<non-prod-tenant-guid>
   SENTINEL_WORKSPACE_RESOURCE_ID=/subscriptions/<sub-guid>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>
   ```

---

## 3. Non-Waivable Safety Gates

The following safety gates **cannot be waived** (`WAIVED_WITH_AUTHOR_EVIDENCE` is rejected):

| Gate ID | Requirement |
| :--- | :--- |
| **`QUAL-00`** | Upstream Validation checklist rollup is `Validated` or `Partially Validated`. |
| **`E2E-G01`** | Real Azure, KQL, and browser providers were used; zero dry-run or simulated fallbacks. |
| **`TK-G02`** | Locked non-production target (`qualification-target.json`) matches authenticated tenant, subscription, and workspace across all steps. |
| **`TK-G03` / `TK-G04`** | Explicit exact-scope authorization and verified effective RBAC/Graph permissions before any read or write. |
| **`TK-G06`** | Approved browser scope for workbook UI checks; `Save`, `Edit`, and destructive portal actions are prohibited. |
| **`TK-G07`** | Privacy and sanitization enforced; no customer PII, credentials, or session tokens exported to `Evidence/`. |
| **`TK-Q11`** | Controlled alert parity restores all Sentinel Analytic Rules and XDR Custom Detections to **disabled** state upon completion or abort. |

---

## 4. Step-by-Step Qualification Flow

### Step 1 — Preflight Target Check & Workflow Initialization (`TK-G02`)

Verify your local `.env` and lock the non-production target into a new `qualification` run:

```powershell
# Inspect configured target without modifying state
sentinel-xdr-migration doctor --solution "Solutions/<SolutionName>"

# Initialize Qualification run and lock qualification-target.json
sentinel-xdr-migration workflow-init `
  --solution "Solutions/<SolutionName>" `
  --workflow-profile qualification `
  --confirm-configured-target `
  --version-bump none `
  --target-version 3.2.2
```

This verifies `az account show` against `AZURE_TENANT_ID` and the derived subscription, resolves the workspace `customerId` via a single exact `az resource show`, and writes `Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/qualification-target.json`.

### Step 2 — Advance Deployment-Scope Planning & Consent (`TK-G03`)

Generate the deterministic local scope plan and record advance planning consent before running discovery/validation:

```powershell
sentinel-xdr-migration plan-deployment `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

sentinel-xdr-migration review-deployment-plan `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>" `
  --expected-plan-sha256 "<planSha256>" `
  --actor "<reviewer-alias>" `
  --approve-component sentinelAlertRules `
  --approve-component xdrCustomDetections `
  --approve-component mockTelemetryIngestion `
  --approve-component fallbackDcr `
  --max-additional-custom-detections <count>
```

> **Note:** Advance planning consent bounds the run's scope; each live write batch (deployment, DCR provisioning, ingestion, alert parity) still requires immediate exact-scope confirmation before execution.

### Step 3 — Discovery, Conversion & Live Runtime KQL Validation (`QUAL-RUNTIME-01`, `TK-Q01`)

Run `inspect` and `convert`, then execute **both** the original Sentinel KQL queries (against Log Analytics) and converted Defender XDR queries (against Microsoft Graph Advanced Hunting):

```powershell
# 1. Inspect and convert
sentinel-xdr-migration inspect --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration convert --solution "Solutions/<SolutionName>" --run-id "<run-id>"

# 2. Plan and approve read-only runtime query execution
sentinel-xdr-migration plan-runtime-query-consent `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

sentinel-xdr-migration review-runtime-query-consent `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>" `
  --approve-family sentinelWorkspaceQueryFamily `
  --approve-family defenderXdrQueryFamily

# 3. Execute live KQL validation against Log Analytics SDK and Graph Advanced Hunting
sentinel-xdr-migration validate-sentinel-sdk `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

sentinel-xdr-migration validate-advanced-hunting `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"
```

- Every query execution is bound to its exact `querySha256` and returns live output schema evidence (`runtime-validation.sentinel.json` and `runtime-validation.graph.json`), verifying all `alertTemplate.customDetails` and entity column bindings (`TK-V04`, `TK-V05`, `TK-Q01`).

### Step 4 — V3.1 Packaging & Official Local Validation (`VAL-CI-01`, `VAL-PKG-01`)

Package the solution with V3.1 and generate the bound `build-and-validate-report.md` receipt:

```powershell
sentinel-xdr-migration package-v3-1 `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>" `
  --version-bump none `
  --target-version 3.2.2

pwsh .script/local-validation/build-and-validate.ps1 `
  -SolutionName "<SolutionName>" `
  -ContentRoot "." `
  -SkipPackaging `
  -PackageReportPath "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/packaging.v3_1.json" `
  -VersionBump none `
  -ValidationSkip ""
```

### Step 5 — Disabled Lab Deployment & Readback (`E2E-Q01`, `E2E-Q02`, `TK-Q02`, `TK-Q07`)

Run deployment preflight, deploy all Sentinel Analytic Rules and Defender XDR Custom Detections **in disabled state**, and verify live readback:

```powershell
# 1. Run deployment & DCR permission preflight
sentinel-xdr-migration preflight-deployment `
  --solution "Solutions/<SolutionName>" `
  --auth-method azure-cli `
  --run-id "<run-id>"

# 2. Deploy disabled Sentinel ARs and Graph XDR CDs with readback verification
sentinel-xdr-migration deploy `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

# 3. Verify full V3.1 ARM template deployment acceptance in Incremental mode
sentinel-xdr-migration plan-arm-template-acceptance-batch `
  --member "Solutions/<SolutionName>::<run-id>" `
  --validation-receipt "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/build-and-validate-report.md" `
  --shared-decisions "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/shared-decisions.json"

sentinel-xdr-migration deploy-arm-template-acceptance-batch `
  --member "Solutions/<SolutionName>::<run-id>" `
  --validation-receipt "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/build-and-validate-report.md" `
  --shared-decisions "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/shared-decisions.json" `
  --expected-batch-plan-sha256 "<batchPlanSha256>" `
  --actor "<approver>" `
  --confirm-exact-scope-write "I approve the exact enumerated ARM template deployment acceptance batch"
```

### Step 6 — Shared Mock Telemetry Ingestion & Row Parity (`QUAL-MOCK-01`, `TK-Q05`, `TK-Q08`)

1. Each AR/CD pair uses **one shared `mock.json` fixture** containing a unique scenario marker and expected match keys (plus separate benign control records).
2. Ingest the shared `mock.json` payload **once** per table/scenario through a compatible solution DCR or an isolated `Custom-*` DCR contract:
   ```powershell
   azure-monitor-logs-ingestion run `
     --contract "<scenario-folder>/ingestion-contract.yaml" `
     --workspace "<locked-workspace-arm-id>" `
     --payload "<scenario-folder>/mock.json" `
     --report "Solutions/<SolutionName>/Logs/sentinel-xdr-migration/<run-id>/ingestion-report.json"
   ```
3. Verify that both the exact Sentinel query and the exact Advanced Hunting query observe the ingested scenario marker and return identical matching row keys before enabling rules for alert parity.

### Step 7 — Controlled Alert Parity (`E2E-Q03`, `TK-Q09`, `TK-Q10`, `TK-Q11`)

Run controlled alert parity across the deployed AR/CD pairs using the already-ingested shared telemetry:

```powershell
# Start controlled parity batch (verifies rules are disabled, then enables pairs for the test window)
sentinel-xdr-migration start-alert-parity-batch `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

# Capture and compare Sentinel and Defender XDR alerts, then restore all rules to disabled
sentinel-xdr-migration complete-alert-parity `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"
```

- Compares alert counts, match keys, severity, MITRE tactics/techniques, entity bindings, custom details, and zero-alert benign controls (`TK-Q09`, `TK-Q10`).
- **Safety Finalizer (`TK-Q11`):** If any error occurs, run `sentinel-xdr-migration abort-alert-parity --solution "Solutions/<SolutionName>" --run-id "<run-id>"` to guarantee all ARs and CDs are returned to `enabled: false`.

### Step 8 — Workbook Live Query & Portal UI Qualification (`E2E-Q04`..`E2E-Q06`, `TK-Q06`)

When the solution includes Workbooks (`Workbooks/` or `XDR Workbooks/`):

```powershell
# 1. Execute every workbook panel/parameter query against live lab telemetry
sentinel-xdr-migration workbook-query-plan --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration workbook-query-review --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration workbook-query-execute --solution "Solutions/<SolutionName>" --run-id "<run-id>"

# 2. Run Playwright browser UI verification (7 interaction kinds: pickers, dependent refresh,
#    filters, drill-down, reload, layout, conditional visibility) and capture screenshots
sentinel-xdr-migration workbook-ui-plan --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration workbook-ui-review --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration workbook-ui-execute --solution "Solutions/<SolutionName>" --run-id "<run-id>"
```

### Step 9 — Generate Qualification Reports & Sanitized `Evidence/` (`E2E-V04`, `TK-G07`)

Evaluate the complete Validation + Qualification + Migration checklists and generate the sanitized PR evidence package:

```powershell
# Evaluate all checklists (Validation + Qualification + Migration)
sentinel-xdr-migration pr-qualify `
  --solution "Solutions/<SolutionName>" `
  --mode full `
  --is-migration `
  --output-dir "Solutions/<SolutionName>/Evidence"

# Generate workflow solution report and curated local PR evidence snapshot
sentinel-xdr-migration solution-report --solution "Solutions/<SolutionName>" --run-id "<run-id>"
sentinel-xdr-migration export-evidence --solution "Solutions/<SolutionName>" --run-id "<run-id>"
```

---

## 5. Generated Artifacts and Rollup Outcomes

Committed evidence under `Solutions/<SolutionName>/Evidence/` includes:
- `Evidence/qualification-report.html` — Reviewer-facing HTML qualification report with check statuses, observed metrics, and links to receipts/screenshots.
- `Evidence/qualification-summary.md` — Markdown rollup summary for the PR body.
- `Evidence/qualification-evidence.json` — Machine-readable check outcomes and SHA-256 bindings.
- `Evidence/receipts/*.json` & `Evidence/screenshots/*.png` — Sanitized verification receipts and portal screenshots (with tenant/subscription GUIDs redacted per `TK-G07`).

| Rollup Outcome | Criteria |
| :--- | :--- |
| **`Qualified`** | `QUAL-00` passes with `Validated`; all applicable checks in `qualification-checks.md` (and live `migration-checks.md` checks if active) are `PASS`, with zero waivers or excluded inventory. |
| **`Conditionally Qualified`** | `QUAL-00` and all non-waivable safety gates (`E2E-G01`, `TK-G02`..`TK-G07`, `TK-Q11`) pass; all other applicable checks pass or are `WAIVED_WITH_AUTHOR_EVIDENCE` (with `--waivers-file`), or upstream Validation is `Partially Validated`. |
