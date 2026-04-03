# Vaikora CrowdStrike AI Agent Security

**Publisher:** Data443 Risk Mitigation, Inc.
**Solution ID:** azure-sentinel-solution-vaikora-crowdstrike
**Version:** 1.0.0

## What This Does

A Microsoft Sentinel Content Hub solution that polls Vaikora for AI agent signals and pushes high-risk actions into CrowdStrike Falcon as Custom IOCs. The Logic App playbook runs every 6 hours, filters to actions where `risk_level` is high or critical, or where `is_anomaly` is true, then calls the CrowdStrike Custom IOC API to create or update indicators.

## Signal Mapping

| Vaikora `risk_level` | CrowdStrike `severity` | CrowdStrike `action` |
|----------------------|------------------------|----------------------|
| critical             | critical               | prevent              |
| high                 | high                   | detect               |
| medium / low         | medium                 | detect               |

Tags added automatically:
- `vaikora`, `ai-agent-security`, `data443` (always)
- `ai-agent-anomaly` — when `is_anomaly` is true
- `ai-threat-detected` — when `threat_detected` is true

IOC type is resolved from action fields in order: `ip_address` / `target_ip` → `ipv4`, `url` / `target_url` → `url`, fallback → `domain`.

Each IOC sets `external_id` to `vaikora-{action_id}` for deduplication.

## Prerequisites

- Microsoft Sentinel workspace
- Vaikora account with API key and agent ID
- CrowdStrike Falcon API client with **Indicators (IOCs): Write** permission

## Files

```
Playbooks/VaikoraToCrowdStrike_Playbook.json   Standalone ARM template for the Logic App
Data/Solution_VaikoraCrowdStrike.json           Solution manifest
Package/mainTemplate.json                       Content Hub deployment template
Package/createUiDefinition.json                 Deployment wizard UI definition
SolutionMetadata.json                           Publisher and category metadata
ReleaseNotes.md                                 Change history
```

## Deployment

### Via Content Hub (recommended)

Install from Microsoft Sentinel Content Hub. Search for "Vaikora CrowdStrike".

### Via ARM template (standalone)

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-file Playbooks/VaikoraToCrowdStrike_Playbook.json \
  --parameters \
      VaikoraApiKey="<your-vaikora-key>" \
      VaikoraAgentId="<your-agent-id>" \
      CrowdStrike_ClientId="<cs-client-id>" \
      CrowdStrike_ClientSecret="<cs-client-secret>"
```

### Via Content Hub package

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-file Package/mainTemplate.json \
  --parameters \
      workspace="<sentinel-workspace-name>" \
      VaikoraApiKey="<your-vaikora-key>" \
      VaikoraAgentId="<your-agent-id>" \
      CrowdStrike_ClientId="<cs-client-id>" \
      CrowdStrike_ClientSecret="<cs-client-secret>"
```

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `VaikoraApiKey` | securestring | — | Vaikora API key (X-API-Key header) |
| `VaikoraAgentId` | string | — | Agent ID to poll |
| `CrowdStrike_BaseUrl` | string | https://api.crowdstrike.com | Falcon API base URL |
| `CrowdStrike_ClientId` | securestring | — | OAuth2 client ID |
| `CrowdStrike_ClientSecret` | securestring | — | OAuth2 client secret |

## Support

support@data443.com — https://www.data443.com
