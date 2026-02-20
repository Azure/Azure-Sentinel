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

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSOCRadar%2FPlaybooks%2FSOCRadar-Alarm-Sync%2Fazuredeploy.json)

You can also install this playbook via **Microsoft Sentinel Content Hub**.

## Prerequisites

- SOCRadar XTI Platform API Key
- Microsoft Sentinel workspace with SOCRadar incidents
- Managed Identity with Sentinel Contributor role
