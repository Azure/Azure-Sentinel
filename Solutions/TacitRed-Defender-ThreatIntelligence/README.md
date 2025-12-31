# TacitRed Defender Threat Intelligence Solution for Microsoft Sentinel

## Overview

The TacitRed Defender Threat Intelligence solution integrates TacitRed's threat intelligence feed with Microsoft Sentinel. It automatically retrieves compromised credentials and other threat indicators from TacitRed and ingests them into Microsoft Sentinel using the Threat Intelligence Upload API for enhanced threat detection.

## Solution Components

| Component | Description |
|-----------|-------------|
| **Playbook** | Logic App that fetches compromised credentials from TacitRed and uploads them to Microsoft Defender Threat Intelligence |

## Prerequisites

- Microsoft Sentinel workspace
- TacitRed API credentials
- Microsoft Defender Threat Intelligence license
- Appropriate RBAC permissions to deploy Logic Apps

## Deployment

1. Navigate to Microsoft Sentinel Content Hub
2. Search for "TacitRed Defender Threat Intelligence"
3. Click Install and follow the deployment wizard
4. Configure the playbook with your TacitRed API credentials

## How It Works

1. The playbook runs on a scheduled trigger
2. It queries TacitRed for recent compromised credential findings
3. For each finding, it creates threat indicators via the Upload API
4. Microsoft Defender can then use these indicators for detection and response

## Support

- **Provider**: Data443 Risk Mitigation, Inc.
- **Email**: support@data443.com
- **Website**: https://www.data443.com

## Learn More

- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel/)
- [TacitRed Platform](https://www.data443.com/tacitred/)
- [Microsoft Defender Threat Intelligence](https://learn.microsoft.com/microsoft-365/security/defender/)
