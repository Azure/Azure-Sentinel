# SOCRadar Alarm Import

Imports SOCRadar XTI platform alarms into Microsoft Sentinel as incidents.

## Features

- Paginated alarm fetching (100 per page)
- Duplicate detection via Sentinel API
- Severity and status mapping
- Optional closed alarm import with classification
- Automatic tagging (SOCRadar, alarm type, sub type)
- Field truncation for large alarms
- Optional audit logging

## Prerequisites

- SOCRadar XTI Platform API Key
- Microsoft Sentinel workspace
- Managed Identity with Sentinel Contributor role

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSOCRadar%2FPlaybooks%2FSOCRadar-Alarm-Import%2Fazuredeploy.json)

You can also install this playbook via **Microsoft Sentinel Content Hub**.
