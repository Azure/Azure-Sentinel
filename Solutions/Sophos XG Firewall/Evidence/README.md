# Reviewer Guide: Sophos XG Firewall (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **Sophos XG Firewall (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow. It follows the same layout as the Azure DDoS Protection reference PR. Every statement below is derived from the run artifacts; where something was not achieved it is reported as such.

**Rollup:** Validation **Validated** / Qualification **Qualified** / Migration **Migration Verified** — overall **Qualified** (73 PASS, 0 FAIL, 0 WAIVED, 4 human-review, 4 N/A of 81)

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
| **Shared Mock Telemetry** | `Sample Data/Tables/Syslog_mock.json` | Synthetic records ingested through the DCR and used for both surfaces. |

---

## 2. Live Lab Receipts (`Evidence/receipts/`)

- **`arm-deployment-readback.json`** — ARM deployment of `Package/mainTemplate.json` (`provisioningState` = `Succeeded`) and the 2 Analytic Rule(s) deployed with `enabled: false`, with the GET snapshot of each rule. Deployment section status: **passed**.
- **`graph-detection-deployment.json`** — Microsoft Graph `/beta/security/rules/detectionRules` upsert of 2 Custom Detection(s): HTTP status, `deployedStatus` (disabled) and content-provenance verification.
- **`alert-parity-live.json`** — the exact Analytic Rule and Custom Detection queries executed on Log Analytics and Defender Advanced Hunting against the ingested mock data (row-level comparison), the per-detection runtime validation results, the mock ingestion summary, and the outcome of the alert-parity attempt. Alert parity: **passed** (2/2 pairs); alert lifecycle: **passed** (2/2 pairs); dual-surface KQL: **passed** (2/2 pairs).
- **`workbook-queries-live.json`** — 10 workbook queries executed live on both surfaces (status **passed**, 10 with rows on both surfaces).
- **`url-and-asset-verification.json`** — URL/asset verification written by the UI agents (URLs: **passed**, assets: **passed**; portal traversal: **passed**).

## 3. Failing Checks and Why

| Check | Status | Observation |
|---|---|---|
| — | `0 FAIL` | None — all 73 applicable automated checks passed (`73 PASS, 0 FAIL, 0 WAIVED, 4 human-review, 4 N/A of 81`), with `E2E-Q02`, `E2E-Q03`, `TK-Q11` (alert parity and alert lifecycle **passed** across 2/2 pairs), `QUAL-DC-01`, and `E2E-V04` all `PASS`. |

### Known gaps
- None — alert parity, alert lifecycle (2/2 rule pairs), data connector queries (`QUAL-DC-01`), and the evidence rollup (`E2E-V04`) all **passed** in `qualification-summary.md` and `pr-qualification-summary.md`.

## 4. Human-Review Sign-Off Items
1. **`QUAL-HR-01`** — Reviewer confirmation of supplied XDR / portal behavioral artifacts
2. **`QUAL-RULE-01`** — Analytic Rule and Hunting Query Semantic Review
3. **`QUAL-TEXT-01`** — Content Explanation and Presentation Review
4. **`QUAL-RELEASE-01`** — Ownership Publication and Removal Review

---

## 5. Re-Running Qualification Locally

```bash
sentinel-xdr-migration pr-qualify --solution "Solutions/Sophos XG Firewall" --run-id "20261021T135411Z-d40dd1e63d834a5dbb134db5a6dd453a" --mode full --is-migration --output-dir "Solutions/Sophos XG Firewall/Evidence/pr-qualification"
```
