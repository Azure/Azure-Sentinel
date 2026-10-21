# Reviewer Guide: CrowdStrike Falcon Endpoint Protection (`3.4.4`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **CrowdStrike Falcon Endpoint Protection (`3.4.4`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (59 PASS, 16 FAIL, 4 human-review, 2 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/CommonSecurityLog_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 2 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 2 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **failed**; alert lifecycle: **failed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — n/a workbook queries executed live on both surfaces (status **not evidenced**, n/a with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **failed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `VAL-URL-01` | Checked 510 URL(s) (102 aka.ms); found 4 invalid URL(s): Data Connectors/Logo/crowdstrike.svg: insecure HTTP URL http://www.w3.org/2000/svg; Data Connectors/CrowdStrikeFa |
| `VAL-DC-01` | Checked 62 connector file(s); issues: Data Connectors/CrowdStrikeFalconAdversaryIntelligence/host.json: missing connector id/title/dataTypes/instructionSteps; Data Connec |
| `E2E-V01` | Total items=94, packaged=17, unacknowledged missing/excluded=77: Data Connectors/Connector_Syslog_CrowdStrikeFalconEndpointProtection.json, Data Connectors/CrowdStrikeAPI |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: VAL-URL-01, VAL-DC-01, E2E-V01. |
| `E2E-Q02` | Evaluated 2 detection(s): initialDisabled=True, totalAlertsFired=0, returnedToDisabled=True. |
| `E2E-Q04` | No live workbook query execution evidence supplied. |
| `E2E-Q05` | UI traversal incomplete: domVerified=False, screenshotCount=11. |
| `QUAL-URL-01` | Checked 64 URL(s); found 2 broken link(s). |
| `QUAL-RUNTIME-01` | Detections SDK True / AH True; workbook queries executed OK on both surfaces: 0/0. |
| `TK-Q11` | alert-parity-state status=failed; alertsFired=0; restoredToDisabled=True; reason=failed to enable parity rules: Custom Detection: Bad request. Please check your input.. |
| `TK-G06` | uiTraversal: failed. |
| `TK-Q06` | uiTraversal: status=failed, screenshots=11, failedItems=['azure-portal-sentinel-workbooks', 'defender-workbook-view']. |
| `TK-Q07` | ARM provisioningState=Succeeded; installationVerified=False; registrationVerified=False; status=arm-accepted-contract-pending. |
| `QUAL-DC-01` | No data-connector query execution receipt exists (dataConnectorIngestion omitted). |
| `E2E-V04` | Passing sections: ['deployment', 'imageRendering', 'mockIngestion']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'uiTraversal', 'urlVerifi |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'alertParityVerified': False, 'dryRun': False, 'failureReason': 'failed to enable parity rules: Custom Detection: B |

### Known gaps
- **Alert lifecycle / alert parity not achieved:** failed to enable parity rules: Custom Detection: Bad request. Please check your input.. Both Analytic Rules and Custom Detections were restored to disabled; `receipts/alert-parity-live.json` records exact-query row parity only (not alert parity).
- **Installed workbook readback missing:** the ARM deployment succeeded, but installation/registration of the packaged (Defender) workbook could not be read back (Graph `security/workbooks` GET returned 403), so `TK-Q07` is reported as FAIL.
- **Data connector queries** were not executed against the lab (`QUAL-DC-01`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/CrowdStrike Falcon Endpoint Protection" --run-id "20261021T163953Z-0cd2a8fa5e76493cbe1d32780572da79" --mode full --is-migration --output-dir "Solutions/CrowdStrike Falcon Endpoint Protection/Evidence/pr-qualification"
```
