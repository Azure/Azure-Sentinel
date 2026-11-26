# Reviewer Guide: Microsoft Entra ID (`3.3.22` Offline Validation & `3.3.20` Baseline Qualification Evidence)

This folder holds the current offline PR validation reports for **Microsoft Entra ID (`3.3.22`)** (packaged via V3.1 without lab deployment), alongside the retained baseline live lab qualification receipts from **`3.3.20`**.

- **`3.3.22` Offline PR Validation Rollup (`Evidence/pr-qualification/`):** Validation **Validated** | Qualification **Not Run** (no lab deployment) | Migration **Not Applicable** — overall **Validated** (`29 Passed | 0 Waived | 0 Human Review Required | 0 Failed | 28 Skipped`, 24 N/A of 81)
- **Historical `3.3.20` Baseline Qualification Rollup (`Evidence/qualification-evidence.json`, `Evidence/receipts/`):** Validation **Validated** | Qualification **Qualified** | Migration **Migration Verified** — overall **Qualified** (`72 Passed | 0 Waived | 4 Human Review Required | 0 Failed`, 5 N/A of 81)

---

## 1. Where to Start (Primary Human-Review Entry Point)

Start your human review by opening **`Evidence/pr-qualification/qualification-report.html`** locally in your browser (or read `Evidence/pr-qualification/qualification-summary.md` on GitHub).

| Artifact | Path | Purpose |
|---|---|---|
| **Interactive HTML Report (Primary Entry Point)** | `Evidence/pr-qualification/qualification-report.html` | Self-contained 4-tab visual report (**Summary & Applicability**, **Validation**, **Qualification**, **Migration & Reviewer Actions**) for **`3.3.22`** offline validation (`Validated`, `0 Failed`). |
| **Markdown PR Summary** | `Evidence/pr-qualification/qualification-summary.md` | GitHub-rendered summary of the **`3.3.22`** offline Validation checklist (`Validated`, Qualification `Not Run`). |
| **Machine-Readable Result** | `Evidence/pr-qualification/pr-qualification-result.json` | All 81 checklist items evaluated against **`3.3.22`** (`checkId`, `status`, `whatWeChecked`, `whatWeObserved`, `whyPassedOrFailed`, `evidenceRefs`). |
| **Sanitized Decision Manifest (Baseline `3.3.20`)** | `Evidence/decision-manifest.json` | Historical sanitized record of reviewed migration and qualification decisions from `3.3.20` (`authorExceptions: []`). |
| **Live Lab Qualification Bundle (Baseline `3.3.20`)** | `Evidence/qualification-evidence.json` | Historical live lab qualification evidence bundle from `3.3.20` (retained unchanged; no lab deployment was run for `3.3.22`). |
| **Workflow State (Baseline `3.3.20`)** | `Evidence/workflow-state.json` | Historical sanitized copy of the `3.3.20` qualification run's `workflow-state.json`. |
| **Raw Live Receipts** | `Evidence/receipts/` | Timestamped JSON receipts for ARM disabled deployment/readback, Graph custom detection creation/readback, dual-surface workbook/connector KQL execution, alert parity, and URL/SVG verification. |
| **Shared Mock Telemetry** | `Sample Data/Tables/*_mock.json` & `Sample Data/SigninLogs_mock.json` | Schema-valid synthetic records covering all 9 Entra ID tables (`SigninLogs`, `AuditLogs`, `AADNonInteractiveUserSignInLogs`, `AADServicePrincipalSignInLogs`, `AADManagedIdentitySignInLogs`, `AADProvisioningLogs`, `AADRiskyUsers`, `AADUserRiskEvents`, `ADFSSignInLogs`). |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and all 74 Analytic Rules and 2 Workbooks deployed with `enabled: false`, with GET readback verification (`resourceCount: 150`).
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert and GET readback of all 74 Custom Detections (`isEnabled: false`) and content-provenance verification.
- **`alert-parity-live.json`** — All 74 Analytic Rule <-> Custom Detection pairs executed across Log Analytics and Defender XDR Advanced Hunting against shared mock telemetry (`pairCount: 74`, `allPairsMatched: true`, `entityParityVerified: true`, `customDetailsParityVerified: true`).
- **`workbook-queries-live.json`** — All 48 workbook KQL queries (`AzureActiveDirectoryAuditLogs.json` and `AzureActiveDirectorySignins.json` across Sentinel and XDR Workbooks) and 26 Data Connector queries (`sampleQueries`, `graphQueries`, `connectivityCriterias`) executed with `ok: true` and `rowCount >= 1`.
- **`url-and-asset-verification.json`** — Verification of all 73 documentation/reference URLs (`HTTP 200`) and 2 SVG logo assets (`AzureActiveDirectory.svg`).

---

## 3. Rollup Summary & Check Counts

- **Validation Status:** `Validated`
- **Qualification Status:** `Qualified`
- **Migration Status:** `Migration Verified`
- **Overall Verdict:** `Qualified`
- **Check Breakdown (81 total / 76 applicable):** `72 Passed | 0 Waived | 4 Human Review Required | 0 Failed | 5 Not Applicable`

---

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Validation / Qualification Locally

Offline validation (no lab deployment):

```powershell
sentinel-xdr-migration pr-qualify `
  --solution "Solutions/Microsoft Entra ID" `
  --mode validation `
  --no-migration
```

Full migration + qualification (requires current live lab receipts):

```powershell
$env:PYTHONPATH = "Tools/SentinelToXDRMigration"
python -m solution_manager.cli pr-qualify `
  --solution "Solutions/Microsoft Entra ID" `
  --mode full `
  --is-migration
```
