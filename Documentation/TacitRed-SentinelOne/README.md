# TacitRed SentinelOne - Solution Documentation

## Overview
**TacitRed SentinelOne** is an automation Playbook designed to push TacitRed threat intelligence indicators directly into the **SentinelOne Singularity** platform. This ensures that threats identified by TacitRed are immediately recognized and blocked/alerted on by SentinelOne agents.

## Capabilities
- **Automated Push**: Sends hashes, domains, and IPs from TacitRed to SentinelOne's Threat Intelligence list.
- **Severity Mapping**: Maps TacitRed severity to SentinelOne exclusion/block lists.
- **Validation**: Includes logic to check if indicators already exist before adding.

## Purpose
Similar to the CrowdStrike solution, this addresses the need for automated defense updates for customers utilizing the SentinelOne EDR platform alongside TacitRed.

## Support & Contact
- **Publisher**: Data443 Risk Mitigation, Inc.
- **Website**: [https://www.data443.com](https://www.data443.com)
- **Support Email**: [support@data443.com](mailto:support@data443.com)
- **Product Page**: [TacitRed](https://www.data443.com/products/tacitred/)

## How to Run / Deploy Manually

### Prerequisites
1.  **TacitRed API Key**.
2.  **SentinelOne API Token**: With privileges to manage Threat Intelligence.

### Manual Deployment via Azure Portal
1.  Use **"Deploy a custom template"** with `Package/mainTemplate.json`.
2.  Fill in the `TacitRed_ApiKey` and `SentinelOne_ApiToken`.
3.  Deploy to your Sentinel Resource Group.

### Manual Deployment via PowerShell
```powershell
New-AzResourceGroupDeployment -ResourceGroupName "YourResourceGroup" `
    -TemplateFile "Package/mainTemplate.json" `
    -TacitRed_ApiKey "..." `
    -SentinelOne_ApiToken "..."
```

## Pull Request
- **PR #13243**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13243)
- **Status**: Active / In Review
