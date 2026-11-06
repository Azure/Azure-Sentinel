# Reviewer Guide: Syslog (`3.2.3`) Qualification Evidence

This folder contains the qualification evidence and PR verification reports for **Syslog (`3.2.3`)** produced by the **Sentinel-to-Defender-XDR Qualification Flow**.

---

## 1. Where to Start (Primary Human-Review Entry Point)

Start your human review by opening **`Evidence/pr-qualification/qualification-report.html`** locally in your browser. All supporting evidence links (`[file]`, `[evidence-bundle]`, `[receipt]`) resolve relative to the solution folder and open in a new tab.

| Artifact | Path | Purpose |
|---|---|---|
| **Interactive HTML Report (Primary Entry Point)** | `Evidence/pr-qualification/qualification-report.html` | Self-contained 4-tab visual report (**Summary & Applicability**, **Validation**, **Qualification**, **Migration & Reviewer Actions**) with the **Reviewer Action Queue**, filterable check cards, and clickable evidence links. |
| **Markdown PR Summary** | `Evidence/pr-qualification/qualification-summary.md` | Quick GitHub-rendered summary of Validation, Qualification, and Migration checklists, rollup verdicts, and human-review sign-off items. |
| **Machine-Readable Result** | `Evidence/pr-qualification/pr-qualification-result.json` | Full structured output of all 81 checklist items (`id`, `status`, `whatWeChecked`, `whatWeObserved`, `whyPassedOrFailed`, `evidenceRefs`). |
| **Sanitized Decision Manifest** | `Evidence/decision-manifest.json` | Sanitized record of reviewed migration and qualification decisions. |
| **Live Lab Qualification Bundle** | `Evidence/qualification-evidence.json` | Consolidated live lab receipts from the non-production Log Analytics workspace and Microsoft Graph (`/v1.0/security/runHuntingQuery` & `/beta/security/rules/detectionRules`). |
| **Raw Live Receipts** | `Evidence/receipts/` | Timestamped JSON responses for ARM template validation/readback, Graph custom detection readback, dual-surface KQL execution, alert parity, and URL/SVG verification. |
| **Shared Mock Telemetry** | `Sample Data/Tables/Syslog_mock.json` | Schema-valid synthetic `Syslog` records covering all packaged Analytic Rules, XDR Custom Detections, and Workbooks. |
