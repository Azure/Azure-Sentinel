# Reviewer Guide: Multi Cloud Attack Coverage Essentials - Resource Abuse (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Multi Cloud Attack Coverage Essentials - Resource Abuse (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validation Failed** / Qualification **Qualification Failed** / Migration **Migration Failed** — overall **Qualification Failed** (46 PASS, 16 FAIL, 4 human-review, 15 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/AWSCloudTrail_mock.json`, `Sample Data/Tables/AWSGuardDuty_mock.json`, `Sample Data/Tables/AlertInfo_mock.json`, `Sample Data/Tables/GCPAuditLogs_mock.json`, `Sample Data/Tables/IdentityInfo_mock.json`, `Sample Data/Tables/SecurityAlert_IPC_mock.json`, `Sample Data/Tables/SecurityAlert_MDATP_mock.json`, `Sample Data/Tables/SecurityAlert_mock.json`, `Sample Data/Tables/SigninLogs_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 9 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 9 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **failed**; alert lifecycle: **failed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — n/a workbook queries executed live on both surfaces (status **not evidenced**, n/a with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **passed**).

## 3. Failing Checks and Why

| Check | Observation |
|---|---|
| `VAL-PKG-02` | Quartet versions: SolutionMetadata.json=3.2.2, Data/Solution_Multi Cloud Attack Coverage Essentials - Resource Abuse.json=3.2.2, ReleaseNotes.md=3.0.3, Package/3.2.2.zip= |
| `E2E-V02` | Valid mock files=0, total records=0; issue: No mock.json found for packaged detections. |
| `QUAL-00` | Validation rollup is 'Validation Failed'; unwaived failing/skipped checks: VAL-PKG-02, E2E-V02. |
| `E2E-Q01` | DCR mock ingestion unverified (verified=False, rowCount=2, simulated=False). |
| `E2E-Q02` | No live alert lifecycle evidence supplied for 18 detection(s). |
| `E2E-Q05` | No UI agent portal traversal or screenshot evidence found. |
| `E2E-Q06` | No UI image/logo/SVG rendering verification evidence supplied. |
| `QUAL-URL-01` | No browser URL verification evidence supplied. |
| `QUAL-MOCK-01` | expected keys landed=False; pairs satisfied=0/9 (not satisfied: ['BrutforceAttemptOnAzurePortalAndAWSConsolAtSameTime', 'Cross-CloudSuspiciousComputeResourcecreationinGCP |
| `TK-Q08` | 0 ingestion report(s): statuses=[], recordsAccepted=0, warnings=[]. |
| `QUAL-RUNTIME-01` | Detections SDK True / AH True; workbook queries executed OK on both surfaces: 0/0. |
| `TK-Q11` | alert-parity-state status=None; alertsFired=0 (per resource: []); initialDisabled=None; restoredToDisabled=False; reason=None. |
| `TK-G06` | uiTraversal: no browser/portal session receipt exists. |
| `TK-Q07` | ARM provisioningState=Succeeded; installationVerified=False; registrationVerified=False; status=arm-accepted-contract-pending. |
| `E2E-V04` | Passing sections: ['deployment']; failing/absent: ['alertLifecycle', 'alertParity', 'dataConnectorIngestion', 'imageRendering', 'mockIngestion', 'uiTraversal', 'urlVerifi |
| `E2E-Q03` | Alert parity unverified (simulated=False, alertParity={'name': 'alertParity', 'status': 'pending', 'attempts': 0, 'startedAt': None, 'completedAt': None, 'message': None, |

### Known gaps
- **Alert lifecycle / alert parity not achieved:** failed to enable parity rules: Defender XDR Custom Detection scheduler did not fire within polling window; restored all rules to disabled.. Both Analytic Rules and Custom Detections were restored to disabled; `receipts/alert-parity-live.json` records exact-query row parity only (not alert parity).
- **Data connector queries** were not executed against the lab (`QUAL-DC-01`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/Multi Cloud Attack Coverage Essentials - Resource Abuse" --run-id "20261025T060713Z-aee97245847d4db4ae719b6807c923db" --mode full --is-migration --output-dir "Solutions/Multi Cloud Attack Coverage Essentials - Resource Abuse/Evidence/pr-qualification"
```
