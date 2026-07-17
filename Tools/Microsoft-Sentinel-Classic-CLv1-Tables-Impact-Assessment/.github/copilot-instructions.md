# Microsoft Sentinel Classic (CLv1) Table Impact Assessment — Copilot Instructions

These instructions apply to **all** Copilot interactions in this repository. They
provide context about the project, coding conventions, and domain knowledge so that
Copilot can give accurate, relevant assistance.

---

## Project overview

PowerShell tool that discovers classic V1 custom log tables (CLv1) in a Microsoft
Sentinel / Log Analytics workspace, assesses dependency impact across all content
types, and maps tables to Content Hub solutions with connector classification.

The **HTTP Data Collector API retires September 14, 2026**. All classic custom log
tables must migrate to DCR-based ingestion before this date. This tool automates
the discovery and impact assessment to support migration planning.

## Repository structure

```
Invoke-TableMigrationReview.ps1           # Main script — single-file entry point
Templates/report.html.template            # Self-contained HTML report template
data/solution-mapping.json                # Static table→solution lookup (auto-updated weekly)
data/update-solution-mapping.mjs          # Node.js script to refresh mapping from upstream CSVs
.github/copilot-instructions.md           # This file — global Copilot context
.github/instructions/powershell.instructions.md  # PowerShell-specific coding conventions
.github/agents/sentinel-migration-assistant.md   # Copilot custom agent for guided execution
.github/workflows/update-solution-mapping.yml    # Weekly GitHub Action to refresh mapping data
LICENSE                                   # MIT License
README.md                                 # Full project documentation
```

## Architecture

### Single-script design

The entire tool is a single PowerShell script (`Invoke-TableMigrationReview.ps1`)
with no external module dependencies beyond `Az.Accounts`. All helper functions are
defined inline. This is intentional — it keeps deployment simple (copy one file).

### Execution flow

1. **Authenticate** — Validates `Az.Accounts` context, refreshes ARM bearer token
2. **Discover** — `GET` workspace tables API, filter `CustomLog` / `Classic`
3. **Assess impact** — Load all content types via ARM, scan for table name references
4. **Map to Content Hub** — Match tables against `data/solution-mapping.json`, classify connectors
5. **Export** — Write CSV, JSON, and HTML reports to the output directory

### Key internal functions

- `Invoke-ArmRequest` — All Azure REST calls go through this wrapper. It handles
  pagination (`nextLink`), token refresh, and error formatting. Never call
  `Invoke-RestMethod` directly.
- `Get-ArmToken` — Retrieves a bearer token from the current `Az.Accounts` context.
- `Write-Step`, `Write-Info`, `Write-Ok`, `Write-Warn2`, `Write-Err` — Formatted
  console output helpers. Never use raw `Write-Host` for status messages.

### Data flow

- **Input**: Azure subscription ID, resource group, workspace name
- **ARM APIs queried**: Tables, Alert Rules, Saved Searches, Workbooks, Logic Apps, DCRs, Content Hub Packages
- **Static data**: `data/solution-mapping.json` (826 tables → 495 solutions, refreshed weekly from Azure-Sentinel upstream)
- **Output**: Pipeline `PSCustomObject` + CSV files + JSON report + HTML report in `OutputPath`

## Domain knowledge

### Classic custom log tables (CLv1)

- Identified by `TableType = CustomLog` and `TableSubType = Classic`
- Always end with `_CL` suffix
- Ingested via the HTTP Data Collector API (retiring September 14, 2026)
- Must be migrated to DCR-based custom tables using the Logs Ingestion API

### Connector classification

When mapping tables to Content Hub solutions, each connector is classified:

- **CCF** — Codeless Connector Framework. Connector ID ends in `CCP`, `CCF`, or `Definition`. Modern, preferred.
- **AMA** — Azure Monitor Agent based. Connector name ends in `Ama`. Modern, preferred.
- **Platform** — Microsoft-native connectors (Azure AD, Office 365, Defender, etc.). Platform-managed.
- **AzureFunctions** — Name contains `Serverless`, `AzureFunction`, or `Polling`. Legacy — should migrate to CCF.
- **Agent** — CEF / Syslog based. Agent-based collection.
- **Legacy** — Anything else. Review manually.

### Content types scanned for impact

- **Analytics Rules** — Scheduled and NRT detection queries (KQL)
- **Hunting Queries** — Proactive threat hunting saved searches (`Category = Hunting Queries`)
- **Parsers** — Workspace functions for normalisation (`Category = Samples` or function-based)
- **Saved Searches** — Log Analytics saved queries
- **Workbooks** — Full serialised JSON walk of all query steps
- **SOAR Playbooks** — Logic App workflow definitions (action body text)
- **Data Collection Rules** — Transform KQL in DCR pipelines

### Azure RBAC

The script is **read-only** and never modifies the workspace. Minimum roles:
- **Microsoft Sentinel Reader** — covers alert rules, content hub, saved searches
- **Monitoring Reader** — covers DCRs
- **Logic App Reader** — covers playbooks
- **Workbook Reader** — covers workbooks (subscription-level)

## Coding conventions

### PowerShell (see also `.github/instructions/powershell.instructions.md`)

- PowerShell 7.0+ required — uses null-coalescing (`??`), `ForEach-Object -Parallel`
- `#Requires` statements for version and module dependencies, not inline checks
- `$ErrorActionPreference = 'Stop'` — fail fast on errors
- All ARM calls go through `Invoke-ArmRequest` — handles pagination and token refresh
- Return structured `[PSCustomObject]` to the pipeline
- Export CSV with `-NoTypeInformation -Encoding UTF8`
- Use the `Write-Step/Info/Ok/Warn2/Err` helpers for console output
- Avoid comments unless explaining complex algorithms
- No build step — the script runs directly

### HTML template

- `Templates/report.html.template` is a self-contained HTML file with inline CSS and JS
- Placeholders use `{{VARIABLE_NAME}}` syntax, replaced by the script at export time
- Must work offline — no external CDN or asset references

### Solution mapping data

- `data/solution-mapping.json` is the static lookup file for mapping tables to Content Hub solutions.
- Source: [Azure-Sentinel Solutions Analyzer](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Solutions%20Analyzer)
- `` fetches upstream CSVs and regenerates the JSON
- Do not edit `solution-mapping.json` manually — it is auto-generated

## Git conventions

- Output directory `./migration-report/` is git-ignored
- `node_modules/` and `.vscode/` are git-ignored
- Commit messages follow conventional commit format (`feat:`, `fix:`, `docs:`, `chore:`)

## What Copilot should NOT do

- Do not suggest breaking the script into multiple module files — the single-file design is intentional
- Do not add `Write-Host` calls — use the existing output helpers
- Do not call `Invoke-RestMethod` directly — use `Invoke-ArmRequest`
- Do not suggest Terraform, Bicep, or ARM template deployments — this is a read-only analysis tool
- Do not suggest modifications to `data/solution-mapping.json` — it is auto-generated
