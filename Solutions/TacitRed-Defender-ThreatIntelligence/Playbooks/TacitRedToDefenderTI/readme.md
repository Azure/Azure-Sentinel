# TacitRed to Defender Threat Intelligence Playbook

## Overview

This playbook automatically synchronizes threat intelligence from TacitRed to Microsoft Defender Threat Intelligence. It retrieves compromised credentials and other threat indicators from TacitRed's API and uploads them to Microsoft Sentinel using the ARM-based createIndicator API.

## Prerequisites

1. **Microsoft Sentinel workspace** - Must be onboarded to Microsoft Sentinel
2. **TacitRed API Key** - Obtain from your TacitRed account
3. **Azure Function App** - Deployed automatically with this solution
4. **RBAC Permissions**:
   - Reader role on the workspace
   - Microsoft Sentinel Contributor role on the workspace

## Deployment

This playbook is deployed automatically as part of the TacitRed Defender Threat Intelligence solution from Microsoft Sentinel Content Hub.

### Manual Deployment

1. Click the **Deploy to Azure** button below
2. Fill in the required parameters:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Target resource group
   - **Workspace**: Your Microsoft Sentinel workspace name
   - **TacitRed API Key**: Your TacitRed API key

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTacitRed-Defender-ThreatIntelligence%2FPlaybooks%2FTacitRedToDefenderTI%2Fazuredeploy.json)

## How It Works

1. **Scheduled Trigger**: The Logic App runs on a configurable schedule (default: every 4 hours)
2. **Fetch Findings**: Calls TacitRed API to retrieve compromised credentials from the last 30 days
3. **Process Data**: The Azure Function App converts findings to STIX format
4. **Upload to Sentinel**: Indicators are uploaded via the ARM-based createIndicator API
5. **Logging**: All operations are logged to Application Insights

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Logic App     │────▶│  Function App   │────▶│ Microsoft       │
│   (Scheduler)   │     │  (Processing)   │     │ Sentinel TI     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   TacitRed      │     │  Application    │
│   API           │     │  Insights       │
└─────────────────┘     └─────────────────┘
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| TacitRed_ApiKey | Your TacitRed API key | Required |
| Domains | Filter by specific domains (empty = all) | [] |
| DateRange | How far back to look for findings | 30 days |

## Troubleshooting

### No indicators appearing in Defender TI

1. Verify the Logic App is running (check Run History)
2. Check Application Insights for Function App errors
3. Verify the workspace is onboarded to Microsoft Sentinel
4. Confirm the Function App MSI has the required roles

### 500 errors from Sentinel API

1. Ensure the workspace is onboarded to Microsoft Sentinel
2. Verify the Function App is using the ARM-based createIndicator API
3. Check that the indicator format is correct

## Support

- **Provider**: Data443 Risk Mitigation, Inc.
- **Email**: support@data443.com
- **Website**: https://www.data443.com

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2025-12-11 | Switched to ARM-based createIndicator API |
| 2.0.0 | 2025-11-10 | Added Function App for processing |
| 1.0.0 | 2025-10-01 | Initial release |
