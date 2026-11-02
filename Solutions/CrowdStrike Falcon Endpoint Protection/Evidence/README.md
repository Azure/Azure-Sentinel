# Reviewer Guide: CrowdStrike Falcon Endpoint Protection (`3.4.4`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **CrowdStrike Falcon Endpoint Protection (`3.4.4`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validated** / Qualification **Conditionally Qualified** / Migration **Conditionally Migrated** — overall **Conditionally Qualified** (69 PASS, 0 FAIL, 6 WAIVED, 4 human-review, 2 N/A of 81)

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
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **waived** (`E2E-Q03`, 5/7 dimensions matched; tactics and entities waived in `Evidence/waivers.json`); alert lifecycle: **passed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — 17 workbook queries executed live on both surfaces (status **passed**, 17 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **waived** (`VAL-URL-01`, `QUAL-URL-01`), assets: **passed**; portal traversal: **passed**).

## 3. Failing and Waived Checks

### Failing Checks (`0 FAIL`)

| Check | Status | Observation |
|---|---|---|
| — | `0 FAIL` | None — all 6 previously failing checks are waived with author evidence (`69 PASS, 0 FAIL, 6 WAIVED, 4 human-review, 2 N/A of 81`). |

### Waived Checks (`6 WAIVED` in `Evidence/waivers.json`)

| Check | Status | Observation / Waiver Summary |
|---|---|---|
| `VAL-URL-01` | `WAIVED` | Pre-existing XML/JSON `$schema` and SVG `xmlns` identifiers (`http://www.w3.org/2000/svg`, `http://schema.management.azure.com/...`, `http://json.schemastore.org/proxies`); all 102 `aka.ms` and navigable HTTPS links passed. |
| `VAL-DC-01` | `WAIVED` | Pre-existing Azure Function runtime/table/DCR files under `Data Connectors/` are not connector definitions; all actual connector definitions passed. |
| `QUAL-URL-01` | `WAIVED` | 62/64 URLs returned HTTP 200; the 2 non-200 strings are the unauthenticated Falcon REST API base URL (`https://api.us-2.crowdstrike.com`) and an AWS SQS queue URL tooltip template (`https://sqs.<region>.amazonaws.com/...`). |
| `QUAL-DC-01` | `WAIVED` | Live third-party CrowdStrike Falcon / AWS S3-SQS source credentials are unavailable in the lab; all 45 connector query entries were probed live on Log Analytics and Advanced Hunting. |
| `E2E-Q03` | `WAIVED` | Live alerts fired on both surfaces (2/2 rules) and matched on 5/7 parity dimensions (`alertCount`, `matchKeys`, `expectedMatches`, `severity`, `evidence`); single-tactic V3.1 schema projection and plain-username Account entity mapping differences are documented in `Evidence/waivers.json`. |
| `E2E-V04` | `WAIVED` | Rollup of evidence sections: `alertLifecycle`, `deployment`, `imageRendering`, `mockIngestion`, `uiTraversal` (45/45 HTTP 200), and `workbookQualification` (17/17) passed; `alertParity`, `dataConnectorIngestion`, and `urlVerification` are covered by waivers `E2E-Q03`, `QUAL-DC-01`, and `QUAL-URL-01`. |

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
