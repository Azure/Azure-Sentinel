# Reviewer Guide: Snowflake (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Snowflake (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (60 PASS, 13 FAIL, 4 human-review, 4 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/SnowflakeLoginV3_CL_mock.json`, `Sample Data/Tables/SnowflakeQueryV3_CL_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 10 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 10 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **failed**; alert lifecycle: **failed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — 13 workbook queries executed live on both surfaces (status **failed**, 8 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `VAL-URL-01` | Checked 364 URL(s) (32 aka.ms); found 2 invalid URL(s): Data Connectors/azuredeploy_Snowflake_API_FunctionApp.json: insecure HTTP URL http[:]//schema.management.azure.com/s |
| `VAL-DC-01` | Checked 18 connector file(s); issues: Data Connectors/AzureFunctionSnowflake/function.json: missing connector id/title/dataTypes/instructionSteps; Data Connectors/host.js |
| `E2E-V01` | Total items=57, packaged=34, unacknowledged missing/excluded=23: Data Connectors/azuredeploy_Snowflake_API_FunctionApp.json, Data Connectors/AzureFunctionSnowflake/functi |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: VAL-URL-01, VAL-DC-01, E2E-V01. |
| `E2E-Q02` | Evaluated 20 detection(s): initialDisabled=True, totalAlertsFired=0, returnedToDisabled=True. |
| `E2E-Q04` | Executed 13 workbook query/queries; totalRows=21, zeroOrFailedQueries=['WB-Q07', 'WB-Q10', 'WB-Q11', 'WB-Q12', 'WB-Q13']. |
| `E2E-Q05` | UI traversal incomplete: domVerified=False, screenshotCount=19. |
| `TK-Q11` | alert-parity-state status=aborted; alertsFired=0 (per resource: [('sentinel-analytic-rule', 0), ('defender-xdr-custom-detection', 0), ('sentinel-analytic-rule', 0), ('def |
| `TK-G06` | uiTraversal: failed. |
| `TK-Q06` | uiTraversal: status=failed, screenshots=19, failedItems=['azure-portal-sentinel-workbooks', 'defender-sentinel-connectors', 'defender-workbook-view']. |
| `QUAL-DC-01` | No data-connector query execution receipt exists (dataConnectorIngestion omitted). |
| `E2E-V04` | Passing sections: ['deployment', 'imageRendering', 'mockIngestion', 'urlVerification']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'uiTra |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'alertParityVerified': False, 'dryRun': False, 'failureReason': 'start-alert-parity-batch parity attempt -> Graph P |

### Known gaps
- **Alert lifecycle / alert parity not achieved:** start-alert-parity-batch parity attempt -> Graph PATCH status=enabled on parser-calling Custom Detection returned HTTP 400 Bad Request (platform limitation; user decision 2026-10-21 17:50, 19:45); cleanup restored all AR/CD disabled. NOTE start-alert-parity-batch x5: every attempt: AR PUT enable ok, CD PATCH enabled -> HTTP 400 Bad Request (platform limitation, parser-based CD); cleanup restored disabled (some attempts hit mgmt.azure.com WinError 10060 during cleanup; final independent readback 18:2x: 10 AR enabled=false, 10 CD disabled). Also ARM/Graph read: defender-workbook-readback.json.. Both Analytic Rules and Custom Detections were restored to disabled; `receipts/alert-parity-live.json` records exact-query row parity only (not alert parity).
- **Workbook queries:** 8/13 returned rows on both surfaces; 13/13 executed without error. Zero-row panels are listed in `receipts/workbook-queries-live.json`.
- **Data connector queries** were not executed against the lab (`QUAL-DC-01`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/Snowflake" --run-id "20261021T143509Z-fc773fd380824ba3be3494efdc61516d" --mode full --is-migration --output-dir "Solutions/Snowflake/Evidence/pr-qualification"
```
