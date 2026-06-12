# 🛡️ Defender Adoption Helper

Assess your **Microsoft Sentinel** environments for readiness to onboard into the **Microsoft Defender portal**.

The tool analyses Defender XDR table retention, analytics rules, and automation rules — then generates an interactive HTML dashboard with actionable findings.

## 🎯 What It Checks

| Area | Checks |
|---|---|
| **Defender Data** | Table retention (30 vs 730 days) — identifies tables that don't need separate ingestion into Sentinel |
| **Analytics Rules** | Fusion engine status, alert visibility, incident reopening, custom alert grouping, Microsoft incident creation rules, disabled rules |
| **Automation Rules** | Incident Provider vs Alert Product Name, Incident Title vs Analytics Rule Name, Fusion dependencies, Description field usage, alert triggers |

Each check is classified as:
- ✅ **OK** — No action needed
- ⚠️ **WARNING** — Requires attention before onboarding
- ℹ️ **INFORMATIONAL** — No action needed, does not block migration (e.g. tables with default retention, disabled rules). Counts as passed in the final score

## 📁 Project Structure

```
├── DefenderAdoptionHelper.ps1          # Main analysis script
├── dashboard.html                      # Interactive HTML dashboard
├── sentinelEnvironments.json           # Workspace configuration file
└── results.csv                         # Generated output (loaded by dashboard)
```

## ⚡ Quick Start

### 1. Configure your workspaces

Edit `sentinelEnvironments.json` with the Sentinel workspaces to analyse:

```json
[
  {
    "subscriptionId": "your-subscription-id",
    "resourceGroupName": "your-resource-group",
    "workspaceName": "your-workspace-name"
  }
]
```

### 2. Run the script

```powershell
# Interactive login (recommended — no app registration needed)
.\DefenderAdoptionHelper.ps1 -EnvironmentsFile .\sentinelEnvironments.json -AuthMode User

# Service principal (client credentials)
.\DefenderAdoptionHelper.ps1 -EnvironmentsFile .\sentinelEnvironments.json -AuthMode App

# Omit -AuthMode to be prompted
.\DefenderAdoptionHelper.ps1 -EnvironmentsFile .\sentinelEnvironments.json
```

### 3. View the dashboard

Open `dashboard.html` in your browser and load the generated `results.csv`.

## 🔐 Authentication

| Mode | Description | Requirements |
|---|---|---|
| **User** | Interactive device code flow via browser | User account with **Microsoft Sentinel Reader** role |
| **App** | Client credentials (service principal) | App Registration with client secret and **Microsoft Sentinel Reader** role |

In **User mode**, the script uses the well-known Azure PowerShell client ID — no app registration is needed. Just sign in with your browser when prompted.

In **App mode**, you need to:
1. Create an **App Registration** in Microsoft Entra ID
2. Generate a **Client Secret** for the app
3. Assign the **Microsoft Sentinel Reader** role to the service principal on each target workspace

## 📊 Dashboard Features

- **Multi-workspace** overview with readiness scores
- **Per-workspace** detailed breakdown by section
- **Multi-select filters** — combine Passed, Warnings, and Informational views
- **Grouped rule checks** — analytics and automation rules grouped by name with individual sub-checks
- **Items Overview** cards per section
- **Pie chart** and score cards for final readiness
- **CSV Data** tab with search and multi-select column filters
- **Export to PDF** — per workspace or all at once
- **Direct links** to Azure portal blades for each section
- **Knowledge base** with recommendations mapped to official Microsoft documentation
- **Multi-tenant guidance** — access models (GDAP, Lighthouse, B2B), MSSP best practices, and known limitations
- **Always-on navigation** — Knowledge base and Multi-Tenant tabs are accessible even before loading a CSV

## 📋 Prerequisites

- PowerShell 5.1+ or PowerShell 7+
- Network access to `management.azure.com` and `login.microsoftonline.com`
- **Microsoft Sentinel Reader** role on the target workspace(s)

## 📚 References

- [Move Microsoft Sentinel to the Defender portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender)

## 👤 Author

**Mario Cuomo** — Microsoft Security  
[LinkedIn](https://www.linkedin.com/in/mariocuomo)
