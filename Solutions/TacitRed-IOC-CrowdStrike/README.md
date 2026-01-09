# TacitRed CrowdStrike IOC Automation Solution for Microsoft Sentinel

## Overview

The TacitRed CrowdStrike IOC Automation solution provides playbooks that demonstrate how to consume TacitRed threat intelligence from Microsoft Sentinel and push indicators of compromise (IOCs) to CrowdStrike Falcon for automated threat response.

## Solution Components

| Component | Description |
|-----------|-------------|
| **Playbook** | Logic App that fetches compromised credentials from TacitRed and creates custom IOC entries in CrowdStrike Falcon |

## Prerequisites

- Microsoft Sentinel workspace
- TacitRed API Key
- CrowdStrike Falcon console access with API credentials (Client ID and Client Secret)
- Appropriate RBAC permissions to deploy Logic Apps

## Deployment

1. Navigate to Microsoft Sentinel Content Hub
2. Search for "TacitRed CrowdStrike"
3. Click Install and follow the deployment wizard
4. Provide the following parameters:
   - **TacitRed API Key**: Your TacitRed API credentials
   - **CrowdStrike Client ID**: Your CrowdStrike API Client ID
   - **CrowdStrike Client Secret**: Your CrowdStrike API Client Secret
   - **CrowdStrike Base URL**: Your CrowdStrike API URL (e.g., https://api.crowdstrike.com)

## How It Works

1. The playbook runs on a scheduled trigger
2. It queries TacitRed for recent compromised credential findings
3. For each finding, it creates a custom IOC entry in CrowdStrike Falcon
4. CrowdStrike can then use these IOCs for detection and response

## Support

- **Provider**: Data443 Risk Mitigation, Inc.
- **Email**: support@data443.com
- **Website**: https://www.data443.com

## Learn More

- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel/)
- [TacitRed Platform](https://data443.com/tacitred-attack-surface-intelligence/)
- [CrowdStrike Falcon Documentation](https://www.crowdstrike.com/resources/)
