# SOCRadar Alarm Sync

Syncs closed Microsoft Sentinel incidents back to SOCRadar with classification mapping.

## Features

- Monitors recently closed SOCRadar-tagged incidents
- Maps Sentinel classification to SOCRadar status
- Synced tag prevents duplicate sync operations
- Configurable polling interval

## Classification Mapping

| Sentinel Classification | SOCRadar Status |
|------------------------|-----------------|
| FalsePositive | FALSE_POSITIVE |
| BenignPositive | MITIGATED |
| TruePositive | RESOLVED |
| Undetermined | RESOLVED |

## Prerequisites

- SOCRadar XTI Platform API Key
- Microsoft Sentinel workspace with SOCRadar incidents
- Managed Identity with Sentinel Contributor role
