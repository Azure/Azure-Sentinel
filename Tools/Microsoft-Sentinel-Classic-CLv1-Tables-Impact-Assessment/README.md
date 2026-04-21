# Microsoft Sentinel Classic (CLv1) Impact Assessment

![PowerShell 7+](https://img.shields.io/badge/PowerShell-7.0%2B-blue?logo=powershell&logoColor=white)
![Az.Accounts 2.13+](https://img.shields.io/badge/Az.Accounts-2.13%2B-0078D4?logo=microsoft-azure&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/github/license/noodlemctwoodle/Sentinel-CLv1-Analyzer)
![Solution Mapping Update](https://github.com/noodlemctwoodle/Sentinel-CLv1-Analyzer/actions/workflows/update-solution-mapping.yml/badge.svg)

Discover, assess, and plan the migration of **Classic Custom Log Tables (CLv1)** in
Microsoft Sentinel before the
[HTTP Data Collector API retirement on **September 14, 2026**](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate).

## Authors
**Toby Goulden**, **Sreedhar Ande**

## Download and run the PowerShell script

1. Download the script 
  
   [![Download]("/Tools/Microsoft Sentinel Classic (CLv1) Impact Assessment/Templates/Download.png")](https://aka.ms/Archive-Logs-Tool-Zip)

2. Extract the folder and open "Configure-Long-Term-Retention.ps1" either in Visual Studio Code/PowerShell

   ***Note***  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  

## Why this tool exists

Microsoft Sentinel workspaces that ingest data via the **Azure Functions based Data connectors**
(using HTTP Data Collector API) store that data in **classic
custom log tables** — identifiable by the `_CL` suffix and a `TableSubType` of
`Classic`. These tables must be migrated to **DCR-based custom tables** before the
API is retired.

Migrating a table is not just a schema change. Analytics rules, hunting queries,
workbooks, parsers, saved searches, SOAR playbooks, and data collection rules may
all reference the table. Changing or removing a table without understanding these
dependencies can silently break detections and response workflows.

This tool automates the discovery and impact assessment so you can plan migrations
with confidence.

## What it does

### Step 1 — Discover classic tables

Queries the workspace Tables API for all tables with `TableType = CustomLog` and
`TableSubType = Classic`. Returns schema metadata including column count, retention
period, and pricing plan for each table.

### Step 2 — Assess dependency impact

For each classic table, scans the following content types for references:

- **Analytics Rules** — scheduled and NRT detection queries
- **Hunting Queries** — proactive threat hunting KQL
- **Parsers** — workspace functions used for normalisation
- **Saved Searches** — Log Analytics saved queries
- **Workbooks** — full serialised JSON walk of all query steps
- **SOAR Playbooks** — Logic App workflow definitions
- **Data Collection Rules** — transform KQL in DCR pipelines

Tables with more dependent items should be prioritised — migrating them requires
updating every reference.

### Step 3 — Map to Content Hub solutions

Matches each table to Content Hub solutions and classifies the data connector
feeding it:

- **CCF** — Codeless Connector Framework (modern, declarative). No migration needed.
- **AMA** — Azure Monitor Agent based. No migration needed.
- **Platform** — Microsoft-native (Azure AD, Office 365, Defender, etc.). Platform-managed, no action required.
- **AzureFunctions** — Legacy serverless polling connector. Plan migration to CCF.
- **Agent** — CEF / Syslog based collection. Review collection method.
- **Legacy** — Anything else. Review manually.

Tables with **no Content Hub solution match** are flagged with a recommendation to
raise a Feature Request with your Microsoft CSAM / SSP.

## Requirements

### Software

- **PowerShell 7.0+**
  - Windows: `winget install Microsoft.PowerShell`
  - macOS: `brew install powershell`
  - Linux: [Install instructions](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-linux)
- **Az.Accounts module 2.13.0+**
  ```powershell
  Install-Module Az.Accounts -MinimumVersion 2.13.0 -Scope CurrentUser
  ```

### Azure RBAC permissions

The script makes **read-only** ARM calls — it never modifies your workspace.

> **Recommended**: Assign **Microsoft Sentinel Reader** + **Monitoring Reader** at the
> resource group scope. This covers all steps with least-privilege access. No write
> permissions are required.

Detailed permissions per step:

- **Authentication** — `Connect-AzAccount` must have an active context with any role on the subscription.
- **Discover tables** — `Microsoft.OperationalInsights/workspaces/tables/read` · **Log Analytics Reader**
- **Analytics Rules** — `Microsoft.SecurityInsights/alertRules/read` · **Microsoft Sentinel Reader**
- **Hunting Queries & Parsers** — `Microsoft.OperationalInsights/workspaces/savedSearches/read` · **Log Analytics Reader**
- **Saved Searches** — same permission as hunting queries · **Log Analytics Reader**
- **Workbooks** — `Microsoft.Insights/workbooks/read` · **Workbook Reader** (subscription-level query; may miss workbooks if scoped to RG only)
- **Playbooks** — `Microsoft.Logic/workflows/read` · **Logic App Reader**
- **DCRs** — `Microsoft.Insights/dataCollectionRules/read` · **Monitoring Reader**
- **Content Hub** — `Microsoft.SecurityInsights/contentPackages/read` · **Microsoft Sentinel Reader**

## Usage

### Interactive

```powershell
./Invoke-TableMigrationReview.ps1
```

Prompts for subscription ID, resource group, and workspace name. Writes all
reports to `./migration-report/`.

### Scripted

```powershell
./Invoke-TableMigrationReview.ps1 `
    -SubscriptionId '00000000-0000-0000-0000-000000000000' `
    -ResourceGroupName 'rg-sentinel' `
    -WorkspaceName 'ws-sentinel' `
    -OutputPath './reports/2026-04' `
    -NonInteractive
```

### Pipeline

The script writes its summary object to the pipeline — capture it for further processing:

```powershell
$result = ./Invoke-TableMigrationReview.ps1 -SubscriptionId $sub -ResourceGroupName $rg -WorkspaceName $ws

$result.ClassicTables | Where-Object { $_.RetentionInDays -gt 90 }
$result.Impacts       | Where-Object { $_.TotalImpacted -gt 0 } | Sort-Object TotalImpacted -Descending
$result.SolutionMatches | Where-Object { $_.MatchCount -eq 0 }
```

## Output

Each run writes five artefacts to `OutputPath`:

- **`tables.csv`** — Discovered classic tables with schema metadata
- **`impact.csv`** — Flat list of every impacted content item, one row per dependency
- **`solution-matches.csv`** — Table-to-Content Hub solution matches with install status
- **`report.json`** — Everything combined in a single file, suitable for further tooling
- **`report.html`** — Self-contained interactive HTML report (open in any browser)

The full `PSCustomObject` is also returned to the pipeline for scripted use.

## Data source

The Content Hub solution mapping is shared with the Next.js web app
(`src/lib/data/solution-mapping.json`) and refreshed weekly by the
`update-solution-mapping.yml` GitHub Action. Both tools stay in sync
automatically.

## Copilot Agent — `Sentinel-CLv1-Impact-Assessment-Assistant`

This repository includes a **GitHub Copilot custom agent** that provides an
end-to-end guided experience for running and interpreting the migration review.

### What the agent does

- **Prerequisite checks** — Verifies PowerShell 7+ and Az.Accounts 2.13.0+ are installed, and guides you through installation if not
- **Parameter collection** — Presents an interactive dialog for Subscription ID, Resource Group, Workspace Name, and Output Path
- **Script execution** — Runs the script in non-interactive mode so you don't need to construct the command yourself
- **Result interpretation** — Explains which tables have the highest dependency impact and should be prioritised
- **Connector classification** — Describes the connector kind (CCF, AMA, Platform, AzureFunctions, Agent, Legacy) and recommended actions
- **Migration guidance** — Advises on next steps for each table, including the September 14 2026 HTTP Data Collector API retirement deadline

### How to use

1. Open this repository in VS Code with GitHub Copilot enabled.
2. Open **Copilot Chat** (`Ctrl+Shift+I` / `Cmd+Shift+I`).
3. Select the **Sentinel-CLv1-Impact-Assessment-Assistant** agent from the agent picker (or type `@Sentinel-CLv1-Impact-Assessment-Assistant`).
4. Ask it to run the migration review — for example:
   - *"Help me run the migration review"*
   - *"Check my workspace for classic custom log tables"*
   - *"What tables need migrating?"*

The agent will walk you through the full workflow: prerequisites → parameters → execution → results.

### Example conversation

```
You:   Help me run the migration review
Agent: [checks PowerShell version and Az.Accounts module]
Agent: [shows interactive dialog for workspace parameters]
Agent: [runs Invoke-TableMigrationReview.ps1 in non-interactive mode]
Agent: Found 2 classic tables. OfficeActivity_CL has 1 dependent item…
```

The agent profile lives at `.github/agents/Sentinel-CLv1-Impact-Assessment-Assistant.md`.

## Contributing

This project ships Copilot configuration to help contributors work effectively:

- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — Global Copilot context covering architecture, domain knowledge, coding conventions, and guardrails
- [`.github/instructions/powershell.instructions.md`](.github/instructions/powershell.instructions.md) — PowerShell-specific coding standards (applied automatically to `*.ps1` files)
- [`.github/agents/Sentinel-CLv1-Impact-Assessment-Assistant.md`](.github/agents/sentinel-migration-assistant.md) — Custom Copilot agent for guided script execution

## Troubleshooting

**`InsufficientPermissions` on Content Hub query**
Requires `Microsoft.SecurityInsights/contentPackages/read` — included in
Microsoft Sentinel Reader role.

**`401 Unauthorized` from ARM**
Run `Connect-AzAccount` and ensure the context points at the tenant containing
the workspace. Token is refreshed automatically on each REST call.

**Workbooks API returns nothing**
The subscription-level query requires `Microsoft.Insights/workbooks/read`. If
you're scoped to RG-only, workbooks may be missed.

### Data source

The Content Hub solution mapping is derived from the
[Azure-Sentinel Solutions Analyzer](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Solutions%20Analyzer)

