# SOCRadar-Alarm-Import

Imports alarms from SOCRadar XTI Platform into Microsoft Sentinel as incidents.

## Features

- Polls SOCRadar API on a configurable interval (default: 5 minutes)
- Pagination support for large alarm volumes
- Duplicate detection via Sentinel API
- Severity mapping (SOCRadar -> Sentinel)
- Three tags per incident: SOCRadar, alarm_main_type, alarm_sub_type
- Field truncation to stay within Sentinel limits
- Optional audit logging to Log Analytics
- Uses Managed Identity (no manual authorization)

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| PlaybookName | Logic App name | SOCRadar-Alarm-Import |
| SocradarApiKey | SOCRadar API Key | (required) |
| CompanyId | SOCRadar Company ID | (required) |
| WorkspaceName | Sentinel Workspace Name | (required) |
| PollingIntervalMinutes | Poll interval (1-1440) | 5 |
| ImportAllStatuses | Import all statuses or OPEN only | false |

## Required Roles

- Microsoft Sentinel Contributor (Resource Group scope)
- Log Analytics Reader (Workspace scope)
