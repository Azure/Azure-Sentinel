# Reviewer Guide: Microsoft Entra ID (`3.3.20`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Microsoft Entra ID (`3.3.20`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR.

**Rollup:** Validation **Validated** | Qualification **Qualified** | Migration **Migration Verified** — overall **Qualified** (`72 Passed | 0 Waived | 4 Human Review Required | 0 Failed`, 5 N/A of 81)

---

## 1. Where to Start (Primary Human-Review Entry Point)

Start your human review by opening **`Evidence/pr-qualification/qualification-report.html`** locally in your browser (or read `Evidence/pr-qualification/qualification-summary.md` on GitHub).

| Artifact | Path | Purpose |
|---|---|---|
| **Interactive HTML Report (Primary Entry Point)** | `Evidence/pr-qualification/qualification-report.html` | Self-contained 4-tab visual report (**Summary & Applicability**, **Validation**, **Qualification**, **Migration & Reviewer Actions**) with the **Reviewer Action Queue**, filterable check cards, and clickable evidence links. |
| **Markdown PR Summary** | `Evidence/pr-qualification/qualification-summary.md` | GitHub-rendered summary of the Validation, Qualification and Migration checklists (`Validated` \| `Qualified` \| `Migration Verified`, `72 Passed \| 0 Waived \| 4 Human Review Required \| 0 Failed`). |
| **Machine-Readable Result** | `Evidence/pr-qualification/pr-qualification-result.json` | All 81 checklist items (`checkId`, `status`, `whatWeChecked`, `whatWeObserved`, `whyPassedOrFailed`, `evidenceRefs`). |
| **Sanitized Decision Manifest** | `Evidence/decision-manifest.json` | Sanitized record of reviewed migration and qualification decisions (`authorExceptions: []`). |
| **Live Lab Qualification Bundle** | `Evidence/qualification-evidence.json` | Consolidated live lab qualification evidence bundle consumed by `pr-qualify`. |
| **Workflow State** | `Evidence/workflow-state.json` | Sanitized copy of the run's `workflow-state.json` reflecting all passed stages. |
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

## 5. Re-Running Qualification Locally

```powershell
$env:PYTHONPATH = "Tools/SentinelToXDRMigration"
python -m solution_manager.cli pr-qualify `
  --solution "Solutions/Microsoft Entra ID" `
  --mode full `
  --is-migration
```
