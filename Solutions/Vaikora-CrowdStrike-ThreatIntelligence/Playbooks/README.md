# Vaikora CrowdStrike Threat Intelligence

**Publisher:** Data443 Risk Mitigation, Inc.
**Solution ID:** azure-sentinel-solution-vaikora-crowdstrike
**Version:** 3.0.0

## What This Does

A Microsoft Sentinel Content Hub solution that polls Vaikora for AI agent behavioral signals and pushes high-risk actions and anomaly detections into CrowdStrike Falcon as Custom IOCs. The Logic App playbook runs on a schedule, filters to actions where `risk_level` is `high` or `critical`, or where `is_anomaly` is `true`, then calls the CrowdStrike Custom IOC API to create or update indicators.

## Signal Mapping

| Vaikora `risk_level` | CrowdStrike `severity` | CrowdStrike `action` |
|----------------------|------------------------|----------------------|
| critical             | critical               | prevent              |
| high                 | high                   | detect               |
| medium / low         | medium                 | detect               |

Tags applied automatically:
- `vaikora`, `ai-agent-security`, `data443` (always)
- `ai-agent-anomaly` when `is_anomaly` is `true`
- `ai-threat-detected` when `threat_detected` is `true`

IOC type is resolved from the action fields: `ip_address` or `target_ip` → `ipv4`, `url` or `target_url` → `url`, fallback → `domain`.

Each IOC sets `external_id` to `vaikora-{action_id}` for deduplication.

## Prerequisites

- Microsoft Sentinel workspace
- Vaikora API Key and Agent ID (obtain from https://vaikora.com)
- CrowdStrike Falcon OAuth2 API client (Client ID, Client Secret, Base URL) with **Indicators (IOCs): Read+Write** scope

## Files

```
Playbooks/VaikoraToCrowdStrike_Playbook.json   Standalone ARM template for the Logic App
Playbooks/Images/                              Deployment screenshots
Data/Solution_VaikoraCrowdStrike.json          Solution manifest
Package/mainTemplate.json                      Content Hub deployment template
Package/createUiDefinition.json                Deployment wizard UI definition
SolutionMetadata.json                          Publisher and category metadata
ReleaseNotes.md                                Change history
```

## Deployment

### Via Content Hub

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
      CrowdStrike_ClientSecret="<cs-client-secret>" \
      CrowdStrike_BaseUrl="<cs-base-url>"
```

## Post Deployment

1. Configure the Vaikora API Key and Agent ID parameters
2. Configure the CrowdStrike Client ID, Client Secret, and Base URL parameters
3. Enable the Logic App and adjust the recurrence trigger as needed

## Test Evidence

Screenshots from a deployment to a test workspace:

- `Playbooks/Images/playbook-template-detail.png` — Sentinel > Automation > Playbook templates rendering with full metadata (description, prerequisites, post-deployment)
- `Playbooks/Images/playbook-create-basics.png` — Create playbook wizard, Basics tab
- `Playbooks/Images/playbook-create-parameters.png` — Create playbook wizard, Parameters tab

## Support

Data443 Risk Mitigation, Inc., support@data443.com
