# Reviewer Guide: Salesforce Service Cloud (`3.7.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Salesforce Service Cloud (`3.7.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validated** / Qualification **Conditionally Qualified** / Migration **Migration Verified** — overall **Conditionally Qualified** (69 PASS, 0 FAIL, 4 WAIVED, 4 human-review, 4 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/SalesforceServiceCloudV3_CL_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 3 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 3 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **passed**; alert lifecycle: **passed**; dual-surface KQL: **passed**.
- **`workbook-queries-live.json`** — 11 workbook queries executed live on both surfaces (status **passed**, 11 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **waived** (`VAL-URL-01`, `QUAL-URL-01`), assets: **passed**; portal traversal: **passed**).

## 3. Failing and Waived Checks

### Failing Checks (`0 FAIL`)

| Check | Status | Observation |
|---|---|---|
| — | `0 FAIL` | None — `QUAL-DC-01` is `PASS` (`3/3` connector queries passed) and 4 checks are waived (`69 PASS, 0 FAIL, 4 WAIVED, 4 human-review, 4 N/A of 81`). |

### Waived Checks (`4 WAIVED` in `Evidence/waivers.json`)

| Check | Status | Observation / Waiver Summary |
|---|---|---|
| `VAL-URL-01` | `WAIVED` | Pre-existing JSON `$schema` identifiers (`http://schema.management.azure.com/...` and `http://json.schemastore.org/proxies`) in unchanged Azure Function connector files; all 23 `aka.ms` and documentation URLs use valid HTTPS. |
| `VAL-DC-01` | `WAIVED` | Pre-existing Azure Function App runtime files (`host.json`, `proxies.json`, `function.json`) under `Data Connectors/`; actual Sentinel Data Connector definitions passed. |
| `QUAL-URL-01` | `WAIVED` | 26/28 URLs returned HTTP 200; the 2 non-200 entries are a customer tenant placeholder (`https://your-domain.my.salesforce.com`) and an upstream marketing URL behind CDN bot protection. |
| `E2E-V04` | `WAIVED` | Rollup of evidence sections: `alertLifecycle`, `alertParity` (3/3 pairs), `dataConnectorIngestion` (`QUAL-DC-01: PASS`, 3/3 connector queries), `deployment`, `imageRendering`, `mockIngestion`, `uiTraversal` (10/10 pages), and `workbookQualification` (11/11 queries) all passed; `urlVerification` is covered by waiver `QUAL-URL-01`. |

### Known gaps
- None — `QUAL-DC-01` is `PASS` (`3/3` connector queries verified in `qualification-summary.md` and `qualification-evidence.json`).

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/Salesforce Service Cloud" --run-id "20261021T135849Z-a87e8352a4124e51867153d6cc93b38d" --mode full --is-migration --output-dir "Solutions/Salesforce Service Cloud/Evidence/pr-qualification"
```
