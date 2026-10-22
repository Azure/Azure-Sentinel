# Reviewer Guide: Zscaler Private Access (ZPA) (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Zscaler Private Access (ZPA) (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validated** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (54 PASS, 19 FAIL, 4 human-review, 4 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/ZPA_CL_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 10 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 10 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **failed**; alert lifecycle: **failed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — 9 workbook queries executed live on both surfaces (status **failed**, 8 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **failed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `QUAL-DEP-01` | Deployment/readback evidence missing or unverified (simulated=False, deployment={'name': 'deployment', 'status': 'pending', 'attempts': 0, 'startedAt': None, 'completedAt |
| `E2E-Q01` | DCR mock ingestion unverified (verified=False, rowCount=2, simulated=False). |
| `E2E-Q02` | No live alert lifecycle evidence supplied for 20 detection(s). |
| `E2E-Q04` | No live workbook query execution evidence supplied. |
| `E2E-Q05` | UI traversal incomplete: domVerified=False, screenshotCount=19. |
| `TK-G02` | qualification-target locked=True; arm-preflight status=None, tenantMatches=None, subscriptionMatches=None, workspaceMatches=None, nonProduction=None; approval target boun |
| `TK-G03` | arm-validation-result: actor=None, approvalReference=None, approvedAt=None, writeAttempted=None, target bound=False. |
| `TK-G04` | armPreflight=False, logAnalytics(SDK 200s)=True, graphHunting(AH 200s)=True, graphCustomDetectionWrite=False. |
| `QUAL-MOCK-01` | expected keys landed=False; pairs satisfied=0/10 (not satisfied: ['ZscalerSharedZPASession', 'ZscalerUnexpectedCountEventResult', 'ZscalerUnexpectedCountries', 'ZscalerUn |
| `TK-Q08` | 0 ingestion report(s): statuses=[], recordsAccepted=0, warnings=[]. |
| `QUAL-RUNTIME-01` | Detections SDK True / AH True; workbook queries executed OK on both surfaces: 0/0. |
| `TK-Q11` | alert-parity-state status=None; alertsFired=0; restoredToDisabled=False; reason=None. |
| `TK-G06` | uiTraversal: failed. |
| `TK-Q06` | uiTraversal: status=failed, screenshots=19, failedItems=['azure-portal-sentinel-workbooks', 'defender-cd-detail:xdr-c4902121-7a7e-44d1-810b-88d26db622ff', 'defender-workb |
| `TK-Q07` | ARM provisioningState=None; installationVerified=None; registrationVerified=None; status=None. |
| `QUAL-PARSER-01` | Parsers=['ZPAEvent']; used by rules=['ZPAEvent']; per-pair row counts (sentinel/xdr)=[(None, None), (None, None), (None, None), (None, None), (None, None), (None, None),  |
| `QUAL-DC-01` | No data-connector query execution receipt exists (dataConnectorIngestion omitted). |
| `E2E-V04` | Passing sections: ['imageRendering', 'urlVerification']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'deployment', 'mockIngestion', 'uiTra |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'name': 'alertParity', 'status': 'pending', 'attempts': 0, 'startedAt': None, 'completedAt': None, 'message': None, |

### Known gaps
- **Alert lifecycle / alert parity not achieved:** failed to enable parity rules: Custom Detection: Bad request. Please check your input.. Both Analytic Rules and Custom Detections were restored to disabled; `receipts/alert-parity-live.json` records exact-query row parity only (not alert parity).
- **Installed workbook readback missing:** the ARM deployment succeeded, but installation/registration of the packaged (Defender) workbook could not be read back (Graph `security/workbooks` GET returned 403), so `TK-Q07` is reported as FAIL.
- **Workbook queries:** 8/9 returned rows on both surfaces; 9/9 executed without error. Zero-row panels are listed in `receipts/workbook-queries-live.json`.
- **Data connector queries** were not executed against the lab (`QUAL-DC-01`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/Zscaler Private Access (ZPA)" --run-id "20261021T130139Z-f4ba5bcd51a84e43bc3be174c7756132" --mode full --is-migration --output-dir "Solutions/Zscaler Private Access (ZPA)/Evidence/pr-qualification"
```
