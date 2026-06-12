# TacitRed SentinelOne IOC Automation Solution for Microsoft Sentinel

## Overview

The TacitRed SentinelOne IOC Automation solution provides playbooks that demonstrate how to consume TacitRed threat intelligence from Microsoft Sentinel and push indicators of compromise (IOCs) to SentinelOne for automated threat response.

## Solution Components

| Component | Description |
|-----------|-------------|
| **Playbook** | Logic App that fetches compromised credentials from TacitRed and creates IOC entries in SentinelOne |

## Prerequisites

- Microsoft Sentinel workspace
- TacitRed API Key
- SentinelOne console access with API token
- SentinelOne Account ID
- Appropriate RBAC permissions to deploy Logic Apps

## Deployment

1. Navigate to Microsoft Sentinel Content Hub
2. Search for "TacitRed SentinelOne"
3. Click Install and follow the deployment wizard
4. Provide the following parameters:
   - **TacitRed API Key**: Your TacitRed API credentials
   - **SentinelOne API Token**: Your SentinelOne API token
   - **SentinelOne Base URL**: Your SentinelOne console URL (e.g., https://usea1-001.sentinelone.net)
   - **SentinelOne Account ID**: Your SentinelOne account identifier

## How It Works

1. The playbook runs on a scheduled trigger
2. It queries TacitRed for recent compromised credential findings
3. For each finding, it creates an IOC entry in SentinelOne
4. SentinelOne can then use these IOCs for detection and response

## Support

- **Provider**: Data443 Risk Mitigation, Inc.
- **Email**: support@data443.com
- **Website**: https://www.data443.com

## Learn More

- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel/)
- [TacitRed Platform](https://data443.com/tacitred-attack-surface-intelligence/)
- [SentinelOne Documentation](https://www.sentinelone.com/docs/)
