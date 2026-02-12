# SOCRadar-Alarm-Sync

Syncs closed incidents from Microsoft Sentinel back to SOCRadar platform.

## Features

- Polls Sentinel for recently closed SOCRadar incidents
- Maps Sentinel classification to SOCRadar status:
  - FalsePositive -> FALSE_POSITIVE (9)
  - BenignPositive -> MITIGATED (12)
  - TruePositive/Undetermined -> RESOLVED (2)
- Syncs severity back to SOCRadar
- Uses "Synced" tag to prevent duplicate syncs
- Pagination for 1000+ incidents
- Uses Managed Identity (no manual authorization)

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| PlaybookName | Logic App name | SOCRadar-Alarm-Sync |
| SocradarApiKey | SOCRadar API Key | (required) |
| CompanyId | SOCRadar Company ID | (required) |
| WorkspaceName | Sentinel Workspace Name | (required) |
| PollingIntervalMinutes | Poll interval (1-1440) | 5 |

## Required Roles

- Microsoft Sentinel Contributor (Resource Group scope)
