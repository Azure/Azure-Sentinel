# Reviewer Guide: Ubiquiti UniFi (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Ubiquiti UniFi (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (61 PASS, 12 FAIL, 4 human-review, 4 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/Ubiquiti_CL_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 10 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 10 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **failed**; alert lifecycle: **failed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — 10 workbook queries executed live on both surfaces (status **failed**, 9 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `VAL-URL-01` | Checked 216 URL(s) (23 aka.ms); found 3 invalid URL(s): Data Connectors/Logo/ubiquiti.svg: insecure HTTP URL http[:]//www.w3.org/2000/svg; Workbooks/Images/Logo/ubiquiti.sv |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: VAL-URL-01. |
| `E2E-Q02` | Evaluated 20 detection(s): initialDisabled=True, totalAlertsFired=0, returnedToDisabled=True. |
| `E2E-Q04` | Executed 10 workbook query/queries; totalRows=51, zeroOrFailedQueries=['WB-Q10']. |
| `E2E-Q05` | UI traversal incomplete: domVerified=False, screenshotCount=19. |
| `QUAL-MOCK-01` | expected keys landed=True; pairs satisfied=9/10 (not satisfied: ['UbiquitiUnknownMacJoined']; zero-row pairs accepted by decision/no declared scenario: ['UbiquitiDestinat |
| `TK-Q11` | alert-parity-state status=failed; alertsFired=0 (per resource: [('sentinel-analytic-rule', 0), ('defender-xdr-custom-detection', 0), ('sentinel-analytic-rule', 0), ('defe |
| `TK-G06` | uiTraversal: failed. |
| `TK-Q06` | uiTraversal: status=failed, screenshots=19, failedItems=['azure-portal-sentinel-workbooks', 'defender-cd-detail:xdr-0998a19d-8451-4cdd-8493-fc342816a197', 'defender-cd-de |
| `QUAL-TI-01` | Scanned 10 Analytic Rule(s) and 10 XDR Detection(s); TI references: ['UbiquitiDestinationInTiList.yaml', 'UbiquitiDestinationInTiList.yaml']. |
| `E2E-V04` | Passing sections: ['dataConnectorIngestion', 'deployment', 'imageRendering', 'mockIngestion', 'urlVerification']; failing/absent: ['alertLifecycle', 'alertParity', 'uiTra |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'alertParityVerified': False, 'dryRun': False, 'failureReason': None, 'matchedPairCount': 0, 'mode': 'live', 'note' |

### Known gaps
- **Workbook queries:** 9/10 returned rows on both surfaces; 10/10 executed without error. Zero-row panels are listed in `receipts/workbook-queries-live.json`.
- **Data connector queries** were not executed against the lab (`QUAL-DC-01`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/Ubiquiti UniFi" --run-id "20261021T130135Z-7898b21ec29c47f49c1966ef8e3a3941" --mode full --is-migration --output-dir "Solutions/Ubiquiti UniFi/Evidence/pr-qualification"
```
