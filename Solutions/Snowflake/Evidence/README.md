# Reviewer Guide: Snowflake (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Snowflake (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (50 PASS, 23 FAIL, 4 human-review, 4 N/A of 81)

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
- **`workbook-queries-live.json`** — 26 workbook queries executed live on both surfaces (status **failed**, 16 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `VAL-URL-01` | Checked 364 URL(s) (32 aka.ms); found 2 invalid URL(s): Data Connectors/azuredeploy_Snowflake_API_FunctionApp.json: insecure HTTP URL http://schema.management.azure.com/s |
| `VAL-DC-01` | Checked 18 connector file(s); issues: Data Connectors/AzureFunctionSnowflake/function.json: missing connector id/title/dataTypes/instructionSteps; Data Connectors/host.js |
| `E2E-V01` | Total items=57, packaged=34, unacknowledged missing/excluded=23: Data Connectors/azuredeploy_Snowflake_API_FunctionApp.json, Data Connectors/AzureFunctionSnowflake/functi |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: VAL-URL-01, VAL-DC-01, E2E-V01. |
| `QUAL-DEP-01` | Deployment/readback evidence missing or unverified (simulated=False, deployment={'name': 'deployment', 'status': 'pending', 'attempts': 0, 'startedAt': None, 'completedAt |
| `E2E-Q01` | DCR mock ingestion unverified (verified=False, rowCount=2, simulated=False). |
| `E2E-Q02` | No live alert lifecycle evidence supplied for 20 detection(s). |
| `E2E-Q04` | No live workbook query execution evidence supplied. |
| `E2E-Q05` | UI traversal incomplete: domVerified=False, screenshotCount=19. |
| `TK-G02` | qualification-target locked=True; arm-preflight status=None, tenantMatches=None, subscriptionMatches=None, workspaceMatches=None, nonProduction=None; approval target boun |
| `TK-G03` | arm-validation-result: actor=None, approvalReference=None, approvedAt=None, writeAttempted=None, target bound=False. |
| `TK-G04` | armPreflight=False, logAnalytics(SDK 200s)=True, graphHunting(AH 200s)=True, graphCustomDetectionWrite=False. |
| `QUAL-MOCK-01` | expected keys landed=False; pairs satisfied=0/10 (not satisfied: ['SnowflakeDiscoveryActivity', 'SnowflakeLongQueryProcessTime', 'SnowflakeMultipleFailedQueries', 'Snowfl |
| `TK-Q08` | 0 ingestion report(s): statuses=[], recordsAccepted=0, warnings=[]. |
| `QUAL-RUNTIME-01` | Detections SDK True / AH True; workbook queries executed OK on both surfaces: 0/0. |
| `TK-Q11` | alert-parity-state status=None; alertsFired=0; restoredToDisabled=False; reason=None. |
| `TK-G06` | uiTraversal: failed. |
| `TK-Q06` | uiTraversal: status=failed, screenshots=19, failedItems=['azure-portal-sentinel-workbooks', 'defender-sentinel-connectors', 'defender-workbook-view']. |
| `TK-Q07` | ARM provisioningState=None; installationVerified=None; registrationVerified=None; status=None. |
| `QUAL-PARSER-01` | Parsers=['Snowflake']; used by rules=['Snowflake']; per-pair row counts (sentinel/xdr)=[(None, None), (None, None), (None, None), (None, None), (None, None), (None, None) |
| `QUAL-DC-01` | No data-connector query execution receipt exists (dataConnectorIngestion omitted). |
| `E2E-V04` | Passing sections: ['imageRendering', 'urlVerification']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'deployment', 'mockIngestion', 'uiTra |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'name': 'alertParity', 'status': 'pending', 'attempts': 0, 'startedAt': None, 'completedAt': None, 'message': None, |

### Known gaps
- **Alert lifecycle / alert parity not achieved:** start-alert-parity-batch parity attempt -> Graph PATCH status=enabled on parser-calling Custom Detection returned HTTP 400 Bad Request (platform limitation; user decision 2026-10-21 17:50, 19:45); cleanup restored all AR/CD disabled. NOTE start-alert-parity-batch x5: every attempt: AR PUT enable ok, CD PATCH enabled -> HTTP 400 Bad Request (platform limitation, parser-based CD); cleanup restored disabled (some attempts hit mgmt.azure.com WinError 10060 during cleanup; final independent readback 18:2x: 10 AR enabled=false, 10 CD disabled). Also ARM/Graph read: defender-workbook-readback.json.. Both Analytic Rules and Custom Detections were restored to disabled; `receipts/alert-parity-live.json` records exact-query row parity only (not alert parity).
- **Installed workbook readback missing:** the ARM deployment succeeded, but installation/registration of the packaged (Defender) workbook could not be read back (Graph `security/workbooks` GET returned 403), so `TK-Q07` is reported as FAIL.
- **Workbook queries:** 16/26 returned rows on both surfaces; 26/26 executed without error. Zero-row panels are listed in `receipts/workbook-queries-live.json`.
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
