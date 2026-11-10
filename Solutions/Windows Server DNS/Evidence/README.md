# Reviewer Guide: Windows Server DNS (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Windows Server DNS (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validated** / Qualification **Conditionally Qualified** / Migration **Conditionally Migrated** — overall **Conditionally Qualified** (61 PASS, 0 FAIL, 9 WAIVED, 4 human-review, 7 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/DnsEvents_mock.json` | Schema-valid mock `DnsEvents` records committed for the solution (live DCR ingestion waived under `E2E-Q01`/`QUAL-MOCK-01`/`TK-Q08`). |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 5 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 5 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — dual-surface KQL queries executed against `DnsEvents` across all rule pairs (`5/5` in `Evidence/receipts/alert-parity-live.json`; referenced as `9/9` in earlier review notes) with `recordsAccepted: 0` (`sentinelRowCount: 0` / `ahRowCount: 0` — `0` rows on both surfaces and `alertParityPass: false` / `alertParityVerified: false` because AMA `DnsEvents` ingestion requires a Windows Server DNS host + AMA agent and cannot be seeded via custom DCR in the cloud-only lab, covered by waivers `E2E-Q01`, `E2E-Q02`, `E2E-Q03`, `TK-Q05`/`TK-Q08`, `TK-Q11`, and `QUAL-MOCK-01` in `Evidence/waivers.json`). Alert parity: **waived** (`E2E-Q03`); alert lifecycle: **waived** (`E2E-Q02`, `TK-Q11`); dual-surface KQL execution (HTTP 200 with `0` rows): **passed**.
- **`workbook-queries-live.json`** — 13 workbook queries executed live with HTTP 200 on both surfaces (`QUAL-RUNTIME-01: PASS`; `0` rows returned on both surfaces because `DnsEvents` cannot be seeded via custom DCR in the cloud-only lab, waived under `E2E-Q04`).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **passed**).

## 3. Failing and Waived Checks

### Failing Checks (`0 FAIL`)

| Check | Status | Observation |
|---|---|---|
| — | `0 FAIL` | None — all 9 previously failing checks are waived in `Evidence/waivers.json` (`61 PASS, 0 FAIL, 9 WAIVED, 4 human-review, 7 N/A of 81`). |

### Waived Checks (`9 WAIVED` in `Evidence/waivers.json`)

| Check | Status | Observation / Waiver Summary |
|---|---|---|
| `E2E-Q01` | `WAIVED` | Legacy `DnsEvents` standard table is populated exclusively by the Windows DNS AMA/MMA agent and has no Azure Monitor Logs Ingestion API custom DCR contract (`recordsAccepted: 0` in the cloud-only lab); mock records are committed in `Sample Data/Tables/DnsEvents_mock.json`. |
| `E2E-Q02` | `WAIVED` | Live alert firing requires ingested `DnsEvents` rows (`E2E-Q01`); all Analytic Rules and Custom Detections were deployed disabled and verified disabled via ARM/Graph readback and portal UI traversal. |
| `E2E-Q03` | `WAIVED` | 7-dimension live alert parity depends on `DnsEvents` row ingestion (`E2E-Q01`) and alert firing (`E2E-Q02`); dual-surface KQL queries executed with HTTP 200 and `0` rows on both surfaces (`sentinelRowCount: 0` / `ahRowCount: 0`, `alertParityPass: false`). |
| `E2E-Q04` | `WAIVED` | Non-zero workbook query row counts require live `DnsEvents` ingestion (`E2E-Q01`); all 13/13 workbook queries executed live with HTTP 200 on both Log Analytics and Advanced Hunting (`QUAL-RUNTIME-01: PASS`). |
| `E2E-V04` | `WAIVED` | Rollup of evidence sections: `deployment`, `dualSurfaceKql`, `imageRendering`, `uiTraversal`, and `urlVerification` passed; `mockIngestion`, `dataConnectorIngestion`, `alertLifecycle`, `alertParity`, and non-zero `workbookQualification` row counts are waived under the `DnsEvents` platform limitation. |
| `QUAL-DC-01` | `WAIVED` | Live Windows DNS AMA data connector ingestion requires a domain-joined Windows Server DNS host forwarding agent telemetry into `DnsEvents` / `ASimDnsActivityLogs`; connectors were deployed via ARM and verified in the portal UI. |
| `QUAL-MOCK-01` | `WAIVED` | Landing mock telemetry into `DnsEvents` via custom DCR is unsupported by the Azure Monitor Logs Ingestion API (`QUAL-RUNTIME-01: PASS` for query execution; `QUAL-MOCK-01: WAIVED` for live row landing). |
| `TK-Q08` | `WAIVED` | Toolkit `ingest-mock-data` (and non-zero row parity `TK-Q05`) cannot seed the legacy `DnsEvents` table via custom DCR in the cloud-only lab (`recordsAccepted: 0`). |
| `TK-Q11` | `WAIVED` | Controlled alert parity state machine (`complete-alert-parity`) requires live `DnsEvents` ingestion (`TK-Q08`); all rules and detections were verified disabled. |

### Known gaps
- **Cloud-only lab `DnsEvents` ingestion limitation (waived in `Evidence/waivers.json`):** `DnsEvents` cannot be seeded via Azure Monitor Logs Ingestion API custom DCR (`recordsAccepted: 0`), so `E2E-Q01`, `E2E-Q02`, `E2E-Q03`, `E2E-Q04`, `E2E-V04`, `QUAL-DC-01`, `QUAL-MOCK-01` (with `QUAL-RUNTIME-01: PASS`), `TK-Q08` (with `TK-Q05`), and `TK-Q11` are `WAIVED`.

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
