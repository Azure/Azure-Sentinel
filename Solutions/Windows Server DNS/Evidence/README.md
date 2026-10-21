# Reviewer Guide: Windows Server DNS (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Windows Server DNS (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (53 PASS, 17 FAIL, 4 human-review, 7 N/A of 81)

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
| **Shared Mock Telemetry** | n/a | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 5 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 5 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **not evidenced**; alert lifecycle: **not evidenced**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — n/a workbook queries executed live on both surfaces (status **not evidenced**, n/a with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `E2E-V02` | Valid mock files=0, total records=0; issue: No mock.json found for packaged detections. |
| `E2E-V03` | Valid mock files=0, total records=0; issue: No workbook mock data JSON found. |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: E2E-V02, E2E-V03. |
| `E2E-Q01` | DCR mock ingestion unverified (verified=False, rowCount=2, simulated=False). |
| `E2E-Q02` | No live alert lifecycle evidence supplied for 10 detection(s). |
| `E2E-Q04` | No live workbook query execution evidence supplied. |
| `E2E-Q05` | UI traversal incomplete: domVerified=False, screenshotCount=14. |
| `QUAL-MOCK-01` | expected keys landed=False; pairs satisfied=0/5 (not satisfied: ['DNS_HighNXDomainCount_detection', 'DNS_HighReverseDNSCount_detection', 'DNS_Miners', 'DNS_TorProxies', ' |
| `TK-Q08` | 0 ingestion report(s): statuses=[], recordsAccepted=0, warnings=[]. |
| `QUAL-RUNTIME-01` | Detections SDK True / AH True; workbook queries executed OK on both surfaces: 0/0. |
| `TK-Q11` | alert-parity-state status=None; alertsFired=0; restoredToDisabled=False; reason=None. |
| `TK-G06` | uiTraversal: failed. |
| `TK-Q06` | uiTraversal: status=failed, screenshots=14, failedItems=['azure-portal-sentinel-workbooks']. |
| `TK-Q07` | ARM provisioningState=Succeeded; installationVerified=False; registrationVerified=False; status=arm-accepted-contract-pending. |
| `QUAL-DC-01` | No data-connector query execution receipt exists (dataConnectorIngestion omitted). |
| `E2E-V04` | Passing sections: ['deployment', 'imageRendering', 'urlVerification']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'mockIngestion', 'uiTra |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'name': 'alertParity', 'status': 'pending', 'attempts': 0, 'startedAt': None, 'completedAt': None, 'message': None, |

### Known gaps
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
sentinel-xdr-migration pr-qualify --solution "Solutions/Windows Server DNS" --run-id "20261021T130124Z-37998be403824c71abed7c30c5d3c765" --mode full --is-migration --output-dir "Solutions/Windows Server DNS/Evidence/pr-qualification"
```
