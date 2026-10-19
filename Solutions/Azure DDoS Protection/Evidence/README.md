# Reviewer Guide: Azure DDoS Protection (`3.2.2`) Qualification Evidence

This folder contains the qualification evidence and PR verification reports for **Azure DDoS Protection (`3.2.2`)** — the first solution produced end-to-end by the **Sentinel-to-Defender-XDR Qualification Flow**.

---

## 1. Where to Start (Primary Human-Review Entry Point)

Start your human review by opening **`Evidence/pr-qualification/qualification-report.html`** locally in your browser. All supporting evidence links (`[file]`, `[evidence-bundle]`, `[receipt]`) resolve relative to the solution folder and open in a new tab.

| Artifact | Path | Purpose |
|---|---|---|
| **Interactive HTML Report (Primary Entry Point)** | `Evidence/pr-qualification/qualification-report.html` | Self-contained 4-tab visual report (**Summary & Applicability**, **Validation**, **Qualification**, **Migration & Reviewer Actions**) with the **Reviewer Action Queue**, filterable check cards, and clickable evidence links that open in a new tab. |
| **Markdown PR Summary** | `Evidence/pr-qualification/qualification-summary.md` | Quick GitHub-rendered summary of Validation, Qualification, and Migration checklists, rollup verdicts, and human-review sign-off items. |
| **Machine-Readable Result** | `Evidence/pr-qualification/pr-qualification-result.json` | Full structured output of all 81 checklist items (`checkId`, `status`, `whatWeChecked`, `whatWeObserved`, `whyPassedOrFailed`, `evidenceRefs`). |
| **Sanitized Decision Manifest** | `Evidence/decision-manifest.json` | Sanitized record of reviewed migration and qualification decisions. |
| **Live Lab Qualification Bundle** | `Evidence/qualification-evidence.json` | Consolidated live lab receipts from `OptimizeSentinelWorkspace` (`76a6cd20-4cd8-4be2-8b97-b9effdc3293f`) and Microsoft Graph (`/v1.0/security/runHuntingQuery` & `/beta/security/rules/detectionRules`). |
| **Raw Live Receipts** | `Evidence/receipts/` | Timestamped raw JSON responses for ARM disabled deployment/readback, Graph custom detection creation/readback, dual-surface KQL execution, alert parity, and URL/SVG verification. |
| **Shared Mock Telemetry** | `Sample Data/Tables/AzureDiagnostics_mock.json` | Schema-valid synthetic `AzureDiagnostics` records covering both legacy (`AdditionalFields`) and Resource-Specific (`ResultDescription`) schemas for `DDoSMitigationReports`, `DDoSMitigationFlowLogs`, and `DDoSProtectionNotifications`. |

---

## 2. How to Review the Evidence (Step-by-Step)

### Step 1: Open `qualification-report.html` & Check the Rollup Verdict
Open `Evidence/pr-qualification/qualification-report.html` in your browser (primary human-review entry point, or view `Evidence/pr-qualification/qualification-summary.md` on GitHub) and verify the three rollup badges:
1. **Validation Status (`Validated`)** — Confirms V3.1 packaging (`Package/3.2.2.zip`), `SolutionMetadata.json`, `ReleaseNotes.md`, Analytic Rule YAML schemas, XDR Custom Detection contracts (`xdr-<GUID>`, `sourceRuleSha256`), and shared mock data (`E2E-V02`, `E2E-V03`).
2. **Qualification Status (`Qualified`)** — Confirms zero simulated fallbacks (`E2E-G01`), disabled ARM/Graph deployment and GET readback (`QUAL-DEP-01`, `TK-Q07`), DCR/table telemetry verification (`E2E-Q01`), controlled alert lifecycle (`E2E-Q02`, `TK-Q11`), workbook KQL execution with `rowCount > 0` (`E2E-Q04`), and asset/URL verification (`E2E-Q06`, `QUAL-URL-01`).
3. **Migration Status (`Migration Verified`)** — Confirms dual-surface KQL execution against both Sentinel Log Analytics and Defender XDR Advanced Hunting (`MIG-Q01`) and strict alert/entity parity (`E2E-Q03`, `MIG-V01..V03`).

### Step 2: Inspect Live Lab Receipts (`Evidence/receipts/`)
Every automated `PASS` in the Qualification and Migration checklists links directly from `qualification-report.html` (opening in a new tab) to a concrete receipt under `Evidence/receipts/`:
- **`arm-deployment-readback.json`**: Verifies that the Sentinel Analytic Rules (`6e76fd9d-8104-41eb-bad3-26054a3ad5f0`, `402a42ad-f31c-48d1-8f80-0200846b7f25`) and Workbook (`AzDDoSStandardWorkbook`) deploy cleanly in disabled state (`enabled: false`) and match GET readback.
- **`graph-detection-deployment.json`**: Verifies that the migrated Defender XDR Custom Detections (`xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0`, `xdr-402a42ad-f31c-48d1-8f80-0200846b7f25`) pass Microsoft Graph `/beta/security/rules/detectionRules` schema validation and remain disabled after testing.
- **`workbook-queries-live.json` & `alert-parity-live.json`**: Confirms that all detection and workbook KQL queries execute with HTTP 200 across both Log Analytics and Defender XDR Advanced Hunting, returning matching entities (`IpAddress = 198.51.100.42`, `DestPublicIpAddress = 203.0.113.10`) for both legacy and Resource-Specific `AzureDiagnostics` schemas.
- **`url-and-asset-verification.json`**: Confirms HTTP 200 and valid SVG dimensions (`75x75`) for `AzDDoS.svg` and documentation links.

### Step 3: Complete the 4 Human-Review Sign-Off Items
The automated runner intentionally marks 4 subjective/governance checks as `HUMAN_REVIEW_REQUIRED` so the PR reviewer can sign off:
1. **`QUAL-HR-01`** — Confirm the supplied XDR / portal behavioral artifacts and receipts.
2. **`QUAL-RULE-01`** — Confirm the detection logic for PPS threshold (`> 10,000 PPS`) and drop-ratio threshold (`> 5%` / `0.05`) matches DDoS operational intent.
3. **`QUAL-TEXT-01`** — Confirm rule descriptions, alert titles, and workbook section descriptions are clear.
4. **`QUAL-RELEASE-01`** — Confirm `ReleaseNotes.md` (`3.2.2`), `SolutionMetadata.json`, and `Package/3.2.2.zip` are ready for release.

---

## 3. Re-Running Qualification Locally

To re-verify the checklist and regenerate the reports at any time:

```bash
PYTHONPATH=Tools/SentinelToXDRMigration python3 -m sentinel_xdr_migration.cli pr-qualify \
  --solution "Solutions/Azure DDoS Protection" \
  --run-id "20261019T141737Z-6024be0bf6084da9ac904cb7cbdafbea" \
  --mode full \
  --is-migration
```
