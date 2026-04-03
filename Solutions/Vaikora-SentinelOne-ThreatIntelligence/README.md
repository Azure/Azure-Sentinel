# Vaikora SentinelOne Threat Intelligence

**Publisher:** Data443 Risk Mitigation, Inc.
**Solution ID:** `azure-sentinel-solution-vaikora-sentinelone`

## Overview

This Microsoft Sentinel solution connects Vaikora AI Agent Security to SentinelOne's Threat Intelligence API. Every 6 hours it polls the Vaikora actions endpoint for high-severity and anomaly detections, maps them to IOCs, and pushes them to SentinelOne for detection and response.

## How it works

1. Logic App fires on a 6-hour recurrence
2. Calls `GET https://api.vaikora.com/api/v1/actions?agent_id=<id>&per_page=100` with `X-API-Key` auth
3. Filters to actions where `severity` is High or Critical, or `is_anomaly` is true
4. On first run, creates a STAR detection rule in SentinelOne scoped to your account
5. Posts each filtered action as an IOC to `/web/api/v2.1/threat-intelligence/iocs`

## IOC Mapping

| Vaikora field      | SentinelOne field  | Notes                                      |
|--------------------|--------------------|--------------------------------------------|
| `log_hash`         | `value`            | Falls back to `agent_id + action_type`     |
| (fixed)            | `type`             | SHA256                                     |
| (fixed)            | `source`           | Vaikora AI Agent Security (Data443)        |
| (fixed)            | `method`           | EQUALS                                     |
| `risk_score`       | `severity`         | 0-30→2, 31-50→3, 51-70→4, 71-85→5, 86-95→6, 96-100→7 |
| `agent_id` + `action_type` + `timestamp` | `externalId` | Prefixed with `vaikora-` |
| All fields         | `description`      | Pipe-delimited context string              |
| (computed)         | `validUntil`       | 90 days from push time                     |

## Parameters

| Parameter             | Type         | Required | Description                                          |
|-----------------------|--------------|----------|------------------------------------------------------|
| `VaikoraApiKey`       | securestring | Yes      | Vaikora API key sent as `X-API-Key`                  |
| `VaikoraAgentId`      | string       | Yes      | Agent ID to poll                                     |
| `SentinelOne_BaseUrl` | string       | Yes      | Console URL, e.g. `https://usea1-021.sentinelone.net`|
| `SentinelOne_ApiToken`| securestring | Yes      | SentinelOne API token                                |
| `SentinelOne_AccountId`| string      | Yes      | Account ID for `filter.accountIds` in all S1 calls   |
| `workspace`           | string       | Yes      | Log Analytics workspace name                         |

## Deployment

Deploy via Microsoft Sentinel Content Hub or use the ARM template directly:

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-file Package/mainTemplate.json \
  --parameters workspace=<workspace-name> \
               VaikoraApiKey=<key> \
               VaikoraAgentId=<agent-id> \
               SentinelOne_BaseUrl=https://usea1-021.sentinelone.net \
               SentinelOne_ApiToken=<token> \
               SentinelOne_AccountId=<account-id>
```

## Support

Data443 Risk Mitigation, Inc. — support@data443.com — https://www.data443.com
