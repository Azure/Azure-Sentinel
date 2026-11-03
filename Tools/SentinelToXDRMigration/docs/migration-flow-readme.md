# Migration Flow Guide (Sentinel-to-Defender-XDR Overlay)

This guide explains how the **Migration Flow** converts Microsoft Sentinel content (`Analytic Rules/` and `Workbooks/`) into paired Defender XDR artifacts (`XDR Detections/` and `XDR Workbooks/`) and how the Migration checklist overlay integrates with the [Validation Flow](validation-flow-readme.md) and [Qualification Flow](qualification-flow-readme.md).

For the formal machine-readable check definitions, see:
- [Migration Overlay Checklist (`migration-checks.md`)](qualification/migration-checks.md)
- [Canonical Agent Workflow (`end-to-end-migration.md`)](../agent-workflows/end-to-end-migration.md)

---

## No-Code / Chat-Based Experience (LLM Agent Orchestration)

**The entire Sentinel-to-Defender-XDR migration can be completed with zero code through natural-language chat** using LLM agents (GitHub Copilot CLI, VS Code Copilot Chat, or Claude Code) powered by the **`XDR Solution Manager`** agent (`.github/agents/xdr-solution-manager.agent.md`) and skills (`sentinel-xdr-end-to-end-orchestrator`, `sentinel-xdr-rule-converter`, `sentinel-xdr-solution-packager`):

- **How it works:** Ask the agent in chat to migrate a solution. The agent runs deterministic discovery and conversion (`Analytic Rules/ -> XDR Detections/`, `Workbooks/ -> XDR Workbooks/`), resolves dependency provenance, collects all review decisions in a single consolidated prompt, builds the V3.1 hybrid package (`>= 3.2.2`), and generates the Migration + Validation (or Qualification) checklist reports.
- **Example Chat Prompts:**
  - *"Migrate `Solutions/<SolutionName>` to Defender XDR, package version `3.2.2`, and generate the validation report."*
  - *"Convert all Analytic Rules and Workbooks in `Solutions/<SolutionName>` to XDR and show me any items that need review."*
  - *"Run `pr-qualify` with the Migration overlay on `Solutions/<SolutionName>`."*

---

## 1. When the Migration Overlay Activates

The Migration overlay (`migration-checks.md`, flag `--is-migration`) activates whenever a pull request introduces or modifies a migration of Microsoft Sentinel content into paired `XDR Detections/` or `XDR Workbooks/` (including edits to the Sentinel source of an existing migrated pair).

- **Overlay architecture:**
  - Static checks (`category: validation`: `TK-V01`..`TK-V05`, `TK-V08`..`TK-V09`, `MIG-WB-01`, `MIG-SAFE-01`) augment the **[Validation Flow](validation-flow-readme.md)** rollup (`Validated` / `Partially Validated`).
  - Live checks (`category: qualification`: `TK-Q01`..`TK-Q03`, `TK-Q05`, `TK-Q09`..`TK-Q10`, `E2E-Q03`) augment the **[Qualification Flow](qualification-flow-readme.md)** rollup (`Qualified` / `Conditionally Qualified`) when `--mode full` or `--mode qualification` is run.
- **PR Label:** `Migration` (paired with `Validation` or `Qualification`, plus `1P Solution`, `ISV Solution`, or `Community Solution`).

---

## 2. Core Conversion Contracts

### 2.1 Analytic Rules $\rightarrow$ `XDR Detections/`

Run `sentinel-xdr-migration convert --solution "Solutions/<SolutionName>" --run-id "<run-id>"` to deterministically convert every Sentinel Analytic Rule YAML into `Solutions/<SolutionName>/XDR Detections/<RuleFile>.yaml`:

| Area | Migration Contract | Check ID |
| :--- | :--- | :---: |
| **Canonical Identity** | `properties.id` is `xdr-<source-sentinel-guid>` with hash-bound source provenance (`sourceRuleId`, `sourceFile`, `sourceSha256`, `sourceQuerySha256`). | `TK-V02` |
| **Disabled by Default** | Every authored and packaged Custom Detection has `enabled: false`. | `VAL-ARTIFACT-01` |
| **NRT & Schedule** | Eligible row-level `NRT` rules convert to Continuous `PT0S` (including supported cosmetic `summarize` rewrites); behavioral aggregations fall back to `PT1H` with documented lookback (`PT4H`). | `TK-V03` |
| **Entity Bindings** | Entity identifiers map to supported Defender XDR entity schemas (`account`, `host`, `ip`, `url`, `file`, `process`, `cloudResource`, etc.). Any source entity field without a 1:1 XDR entity equivalent is additionally preserved in `alertTemplate.customDetails`. | `TK-V04`, `TK-V05` |
| **MITRE ATT&CK** | Authored YAML preserves **all** source MITRE tactics and compatible techniques; ARM/Graph deployment payloads project the first tactic until multi-tactic API support is enabled. | `TK-V08` |
| **`SecurityAlert` / `SecurityIncident`** | Deterministically rewritten to `AlertInfo` + `| join kind=leftouter AlertEvidence on AlertId`, using `coalesce(tostring(column_ifexists("ResourceID", "")), tostring(column_ifexists("AzureResourceId", "")))` for cross-surface compatibility. | `TK-V09` |
| **ASIM & `_GetWatchlist`** | Built-in ASIM parsers starting with `_` (`_ASim_*`, `_Im_*`) and `_GetWatchlist` are supported in Advanced Hunting and Custom Detections. `Watchlist` is platform reference data, not a required data connector. | `TK-V06` |
| **Content Version** | Migrated content inherits the solution release version ($\ge 3.2.2$ and $< 4.0.0$). | `TK-V10`, `TK-V11` |

### 2.2 Workbooks $\rightarrow$ `XDR Workbooks/`

- **Clean Public Contract (`public-workbook-v1`):** Authored workbooks under `XDR Workbooks/<relative-path>.json` retain the complete `Notebook/1.0` structure, migrated Advanced Hunting / cross-surface queries, and clean `contentProvenance` (`requiredWorkloads`, `requiredDataConnectors`, `requiredWorkspaceFunctions`).
- **Local Proof Separation:** Reviewer identities, session context, and query-conversion histories stay in Git-ignored `Logs/sentinel-xdr-migration/<run-id>/` via `workbook-publication-clean`.

### 2.3 ISV & Connector Protection (`MIG-SAFE-01`)

When packaging a migrated solution with `package-v3-1`, existing Sentinel resources (`Data Connectors/`, `Parsers/`, `Hunting Queries/`, `Playbooks/`, `Analytic Rules/`, `Workbooks/`) are preserved intact:
- `Package/mainTemplate.json` must be strictly additive for XDR resources (`CustomDetection_xdr-*` and `DefenderWorkbook_*` gated behind `E5Flavor`).
- Any regression or removal of existing Sentinel Data Connectors, DCRs, or CCF definitions fails `MIG-SAFE-01`.

---

## 3. Evidence-Based Partial Selection (`> 50%` Rule)

If a solution contains source Analytic Rules that cannot yet be validated or converted (for example, rules depending on unavailable third-party schemas), maintainers can package the validated subset using `package-selection-plan` and `package-selection-apply`:

```powershell
sentinel-xdr-migration package-selection-plan `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>"

sentinel-xdr-migration package-selection-apply `
  --solution "Solutions/<SolutionName>" `
  --run-id "<run-id>" `
  --expected-plan-sha256 "<plan-sha256>"
```

- **Eligibility Threshold:** Validated, unique source-rule IDs represented by deployable Custom Detections must be **strictly greater than 50%** (`2 * validated > original`) of the complete recursive Sentinel Analytic Rule inventory.
- **Rollup Impact:** Packaging a subset with acknowledged exclusions in `decision-manifest.json` passes `E2E-V01` / `TK-V01` with explicit exclusion accounting and forces the overall rollup to **`Partially Validated`** (or **`Conditionally Qualified`** if live Qualification is run on the selected subset).

---

## 4. Running the Migration Checklist Evaluation

```powershell
# Migration + Validation Flow (Offline / CI)
sentinel-xdr-migration pr-qualify `
  --solution "Solutions/<SolutionName>" `
  --mode validation `
  --is-migration

# Migration + Qualification Flow (Live Non-Prod Lab)
sentinel-xdr-migration pr-qualify `
  --solution "Solutions/<SolutionName>" `
  --mode full `
  --is-migration
```
