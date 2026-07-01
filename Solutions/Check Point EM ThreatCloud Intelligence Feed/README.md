# Check Point EM ThreatCloud Intelligence Feed — Microsoft Sentinel Solution

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/checkpoint.svg" width="75px" height="75px">

## Overview

This solution streams the **Check Point Exposure Management** (Infinity External Risk Management / Argos) ThreatCloud Intelligence Feed into Microsoft Sentinel and provides an out-of-the-box (OOTB) enrichment playbook for Sentinel incident entities.

### What's included

| Component | Description |
|-----------|-------------|
| **Data Connector** (CCP) | Polls the Check Point EM ThreatCloud Intelligence Feed API on a recurrence and ingests indicators (IPs, domains, URLs, file hashes) with confidence, severity, malicious classification, kill-chain stage, blocking and uniqueness flags, malware types, and CVE/campaign associations into `emiocintel_CL`. |
| **Playbook** `CPEM_IOCIntelligenceEnrichment` | Triggers on Microsoft Sentinel incident webhook; enriches IP / FileHash / Domain / URL entities against the same API and appends a structured enrichment comment to the incident. |

## Prerequisites

Before deploying this solution:

1. **Microsoft Sentinel must be enabled on the target Log Analytics workspace.** Enabling Sentinel auto-provisions the Data Collection Endpoint (DCE) that this solution's CCP data connector relies on. Without Sentinel enabled, the `Microsoft.Insights/dataCollectionRules` resource in this template fails to deploy with a "DCE not found" error.
   - To enable Sentinel: in the Azure Portal, navigate to **Microsoft Sentinel** → **Add** → select your Log Analytics workspace → **Add**.
   - This is the same prerequisite that applies to the sibling **Check Point Cyberint IOC** and **Check Point Cyberint Alerts** solutions.

2. **Check Point Exposure Management API access:** a valid Argos URL (e.g. `https://your-tenant.cyberint.io`), API access token, and the Customer Name registered with your Cyberint account.

3. **Permissions:** the deploying principal needs Microsoft Sentinel Contributor (or equivalent) on the workspace and the resource group.

## Deployment

Two supported paths:

- **Content Hub (recommended for customers):** Microsoft Sentinel → Content Hub → search "Check Point EM ThreatCloud Intelligence Feed" → Install. The connector setup UI walks you through configuring the API token and other parameters; Sentinel handles the DCE wiring.
- **ARM direct (for automation / GitOps):** deploy `Package/mainTemplate.json` against a Sentinel-enabled workspace. The DCE referenced by the DCR is the workspace's auto-provisioned endpoint, so it must exist before deployment (see Prerequisite #1).

## Support

- **Provider:** Check Point
- **Tier:** Partner
- **Contact:** [Check Point Support](https://www.checkpoint.com/support-services/contact-support/)
