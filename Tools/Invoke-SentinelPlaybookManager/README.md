# Invoke-SentinelPlaybookManager

> *One Script to rule them all, One Script to find them,*
> *One Script to bring them all, and in the SOC bind them.*

A PowerShell 7 tool that exports Microsoft Sentinel playbooks from any Azure resource group, sanitises them into fully portable ARM templates, and optionally deploys them to any target environment — all in a single command.

## Features

- **Export** — Discovers all Logic App playbooks and their API connections, exports via Azure Resource Manager
- **Sanitise** — Comprehensive ARM template cleanup for cross-environment portability:
  - Replaces all hardcoded subscription IDs, resource groups, locations, and tenant IDs
  - Normalises managed API connector names (lowercase, strips designer suffixes)
  - Configures managed identity only on supported APIs (azuresentinel, keyvault)
  - Deduplicates connection resources and `$connections` workflow parameters
  - Fixes ARM expression escaping (STIX patterns, encodeURIComponent, semicolons)
  - Enforces Azure 80-character connection name limits
  - Sanitises PlaybookName for valid ARM resource name characters
  - Parameterises tag values for cost tracking and governance
  - Auto-detects workflow-level parameters and wires ARM passthrough
  - Populates ARM template metadata (title, trigger type, entities, connectors, timestamps)
  - Upgrades API versions to latest stable (Logic Apps `2019-05-01`, Connections `2016-06-01`)
- **Deploy** — Integrated deployment to any target resource group with environment parameter injection
- **Interactive Selection** — Optional GUI picker via `Out-ConsoleGridView` (graceful fallback if not installed)
- **Environment Configuration** — Auto-generates `environment.parameters.json` for customer value population

## Prerequisites

| Requirement | Install |
|-------------|---------|
| PowerShell 7+ | [Install PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) |
| Az PowerShell module | `Install-Module Az -Scope CurrentUser` |
| Az.LogicApp module | `Install-Module Az.LogicApp -Scope CurrentUser` |
| ConsoleGuiTools *(optional, for `-Interactive`)* | `Install-Module Microsoft.PowerShell.ConsoleGuiTools -Scope CurrentUser` |

You must be authenticated to Azure before running the script:

```powershell
Connect-AzAccount
```

## Quick Start

```powershell
# Export all playbooks from a resource group
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel"

# Export and deploy in one command
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-source" `
    -Deploy -TargetResourceGroupName "rg-target" `
    -EnvironmentFile "./environment.parameters.json"
```

## Usage Examples

### Export all playbooks

```powershell
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel"
```

Exports every Logic App in the resource group to `./Playbooks/Exported/<PlaybookName>/azuredeploy.json` with a generated `environment.parameters.json`.

### Interactive selection

```powershell
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -Interactive
```

Opens a terminal grid view where you can select specific playbooks with Space and confirm with Enter.

### Filter by name pattern

```powershell
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -PlaybookFilter "Incident-*"
```

Exports only playbooks matching the wildcard pattern.

### Export + Deploy (one shot)

```powershell
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-source" `
    -Deploy -TargetResourceGroupName "rg-target" `
    -EnvironmentFile "./my-env.json"
```

Exports from the source RG, sanitises, then immediately deploys to the target RG using values from the environment file.

### Export templates only (for gallery/repo)

```powershell
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -SkipParameterFiles
```

Outputs only `azuredeploy.json` files — no parameter files generated. Ideal for publishing to a Sentinel content gallery or Git repository.

### Custom output path

```powershell
.\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -OutputPath "./MyExport"
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `ResourceGroupName` | Yes | — | Source Azure resource group containing the playbooks |
| `OutputPath` | No | `./Playbooks/Exported` | Directory for exported templates |
| `Interactive` | No | `$false` | Open GUI picker for playbook selection |
| `PlaybookFilter` | No | `*` | Wildcard filter for playbook names |
| `SkipParameterFiles` | No | `$false` | Skip generating parameter and environment files |
| `Deploy` | No | `$false` | Deploy exported templates after export |
| `TargetResourceGroupName` | No* | — | Target RG for deployment (*required with `-Deploy`) |
| `EnvironmentFile` | No | Auto-generated | Path to environment.parameters.json for deployment |

## Output Structure

```
OutputPath/
├── environment.parameters.json      # Master config — fill in for your environment
├── PlaybookA/
│   ├── azuredeploy.json              # Sanitised ARM template
│   └── azuredeploy.parameters.json   # Per-playbook parameter file
├── PlaybookB/
│   ├── azuredeploy.json
│   └── azuredeploy.parameters.json
└── ...
```

## Environment Parameters File

The script auto-generates `environment.parameters.json` with all unique parameters discovered across all exported templates. Fill in the values for your target environment:

```json
{
  "_readme": "Fill in the values below for your target environment.",
  "ManagedIdentityName": "my-soar-managed-identity",
  "_ManagedIdentityName": "Value for ManagedIdentityName.",
  "NotificationEmailAddress": "soc-alerts@company.com",
  "_NotificationEmailAddress": "Value for NotificationEmailAddress.",
  "TagBusinessUnit": "Security",
  ...
}
```

Keys prefixed with `_` are descriptions and are ignored by the script. Parameters with ARM function defaults (`SubscriptionId`, `ResourceGroupName`, `TenantId`) are omitted — they auto-resolve at deploy time.

## Workflow

```
┌──────────────────────┐
│  Source Resource     │
│  Group (Azure)       │
└─────────┬────────────┘
          │ Export-AzResourceGroup
          ▼
┌──────────────────────┐
│  Sanitise            │
│  - Parameterise      │
│  - Normalise APIs    │
│  - Fix expressions   │
│  - Add metadata      │
│  - Upgrade versions  │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Output              │
│  azuredeploy.json    │  ──── Gallery / Git repo
│  + parameters.json   │
│  + environment.json  │
└─────────┬────────────┘
          │ -Deploy (optional)
          ▼
┌──────────────────────┐
│  Target Resource     │
│  Group (Azure)       │
└──────────────────────┘
```

## Known Limitations

| Issue | Cause | Workaround |
|-------|-------|------------|
| Custom API connectors fail to deploy | `/customApis/` connectors must be pre-deployed in the target | Deploy the custom connector before the playbook |
| Forbidden errors on some connectors | Test SP lacks API permissions (e.g., VirusTotal, MDE, Teams) | Grant connector API permissions to the deploying identity |
| Cross-template connection references | Some playbooks reference connections from other playbooks | Deploy dependency playbooks first |
| Embedded JSON literal expressions | Hardcoded JSON arrays in Compose actions that ARM misinterprets | Manual template fix required |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.1 | April 2026 | Initial release — export, sanitise, deploy, interactive selection, metadata population |

## Author

**Toby G** — April 2026

## License

Internal use. Not for redistribution without permission.
