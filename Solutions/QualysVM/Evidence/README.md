# Reviewer Guide: QualysVM (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **QualysVM (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (62 PASS, 13 FAIL, 4 human-review, 2 N/A of 81)

---

## 1. Where to Start

Open **`Evidence/pr-qualification/qualification-report.html`** in a browser (or read `qualification-summary.md` on GitHub).

| Artifact | Path | Purpose |
|---|---|---|
| **Interactive HTML Report** | `Evidence/pr-qualification/qualification-report.html` | Self-contained report with the Reviewer Action Queue and per-check cards. |
| **Markdown PR Summary** | `Evidence/pr-qualification/qualification-summary.md` | GitHub-rendered summary of the Validation, Qualification and Migration checklists. |
| **Machine-Readable Result** | `Evidence/pr-qualification/pr-qualification-result.json` | All 81 checklist items (`checkId`, `status`, `whatWeChecked`, `whatWeObserved`, `whyPassedOrFailed`, `evidenceRefs`). |
| **Sanitized Decision Manifest** | `Evidence/decision-manifest.json` | Sanitized record of reviewed migration and qualification decisions. |
| **Live Lab Qualification Bundle** | `Evidence/qualification-evidence.json` | Evidence sections consumed by `pr-qualify`; every section lists the source artifacts and their sha256 (`sourceReceipts`, run-directory files that are not committed). |
| **Workflow State** | `Evidence/workflow-state.json` | Sanitized copy of the run's `workflow-state.json` (unmodified; reflects the real stage statuses). |
| **Raw Live Receipts** | `Evidence/receipts/` | The five receipts described in section 2. |
| **Shared Mock Telemetry** | `Sample Data/Tables/QualysHostDetectionV3_CL_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 2 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 2 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **failed**; alert lifecycle: **failed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — 14 workbook queries executed live on both surfaces (status **failed**, 12 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **failed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `VAL-DC-01` | Checked 8 connector file(s); issues: Data Connectors/AzureFunctionQualysVM_V2/function.json: missing connector id/title/dataTypes/instructionSteps; Data Connectors/host.j |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: VAL-DC-01. |
| `E2E-Q02` | Evaluated 4 detection(s): initialDisabled=True, totalAlertsFired=0, returnedToDisabled=True. |
| `E2E-Q04` | Executed 14 workbook query/queries; totalRows=74, zeroOrFailedQueries=['WB-Q05', 'WB-Q07']. |
| `E2E-Q05` | No UI agent portal traversal or screenshot evidence found. |
| `QUAL-URL-01` | Checked 35 URL(s); found 1 broken link(s). |
| `TK-Q11` | alert-parity-state status=failed; alertsFired=0; restoredToDisabled=True; reason=parity attempt: Sentinel AR enabled then CD enable BadRequest; cleanup restored both disa |
| `TK-G06` | uiTraversal: no browser/portal session receipt exists. |
| `TK-Q06` | uiTraversal: no ui/ui-portal-traversal.json receipt exists. |
| `TK-Q07` | ARM provisioningState=Succeeded; installationVerified=False; registrationVerified=False; status=arm-accepted-contract-pending. |
| `QUAL-DC-01` | No data-connector query execution receipt exists (dataConnectorIngestion omitted). |
| `E2E-V04` | Passing sections: ['deployment', 'imageRendering', 'mockIngestion']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'uiTraversal', 'urlVerifi |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'alertParityVerified': False, 'dryRun': False, 'failureReason': 'parity attempt: Sentinel AR enabled then CD enable |

### Known gaps
- **Alert lifecycle / alert parity not achieved:** parity attempt: Sentinel AR enabled then CD enable BadRequest; cleanup restored both disabled; diagnostic PATCH of CD 3edb7215 query to table-based text then restored original (queryText verified identical), CD left disabled -> Graph CD enable fails when query references workspace function QualysHostDetection; passes when query uses underlying table. Both Analytic Rules and Custom Detections were restored to disabled; `receipts/alert-parity-live.json` records exact-query row parity only (not alert parity).
- **Installed workbook readback missing:** the ARM deployment succeeded, but installation/registration of the packaged (Defender) workbook could not be read back (Graph `security/workbooks` GET returned 403), so `TK-Q07` is reported as FAIL.
- **Workbook queries:** 12/14 returned rows on both surfaces; 14/14 executed without error. Zero-row panels are listed in `receipts/workbook-queries-live.json`.
- **Data connector queries** were not executed against the lab (`QUAL-DC-01`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/QualysVM" --run-id "20261021T133203Z-34b123410ce4410b8bca9c80838a1912" --mode full --is-migration --output-dir "Solutions/QualysVM/Evidence/pr-qualification"
```
