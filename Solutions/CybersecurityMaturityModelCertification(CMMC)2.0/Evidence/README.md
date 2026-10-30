# Reviewer Guide: CybersecurityMaturityModelCertification(CMMC)2.0 (`3.2.2`) Qualification Evidence

This folder holds the qualification evidence and PR verification reports for **CybersecurityMaturityModelCertification(CMMC)2.0 (`3.2.2`)**, produced by the Sentinel-to-Defender-XDR Qualification Flow.

**Rollup:** Validation **Validated** | Qualification **Qualified** | Migration **Migration Verified** — overall **Qualified** (`0 Waived | 0 Failed`)

---

## 1. Where to Start (Primary Human-Review Entry Point)

Start your human review by opening **`Evidence/pr-qualification/qualification-report.html`** locally in your browser (or read `Evidence/pr-qualification/qualification-summary.md` on GitHub).

| Artifact | Path | Purpose |
|---|---|---|
| **Interactive HTML Report (Primary Entry Point)** | `Evidence/pr-qualification/qualification-report.html` | Self-contained 4-tab visual report (**Summary & Applicability**, **Validation**, **Qualification**, **Migration & Reviewer Actions**) with filterable check cards and clickable evidence links. |
| **Markdown PR Summary** | `Evidence/pr-qualification/qualification-summary.md` | GitHub-rendered summary of the Validation, Qualification and Migration checklists (`Validated` \| `Qualified` \| `Migration Verified`). |
| **Machine-Readable Result** | `Evidence/pr-qualification/pr-qualification-result.json` | All checklist items (`checkId`, `status`, `whatWeChecked`, `whatWeObserved`, `whyPassedOrFailed`, `evidenceRefs`). |
| **Sanitized Decision Manifest** | `Evidence/decision-manifest.json` | Sanitized record of reviewed migration and qualification decisions (`authorExceptions: []`). |
| **Live Lab Qualification Bundle** | `Evidence/qualification-evidence.json` | Consolidated live lab qualification evidence bundle consumed by `pr-qualify`. |
| **Workflow State** | `Evidence/workflow-state.json` | Sanitized copy of the run's `workflow-state.json` reflecting all passed stages. |
| **Raw Live Receipts** | `Evidence/receipts/` | Timestamped JSON receipts for ARM disabled deployment/readback, Graph custom detection deployment/readback, dual-surface KQL & alert parity execution, workbook query execution, and URL/SVG verification. |
| **Shared Mock Telemetry** | `Sample Data/Tables/*_mock.json` & `Sample Data/*_mock.json` | Schema-valid synthetic records covering all 12 referenced tables (`SecurityRegulatoryCompliance`, `DeviceTvmSecureConfigurationAssessment`, `SigninLogs`, `AuditLogs`, etc.). |
