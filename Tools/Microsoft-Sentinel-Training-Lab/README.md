# Welcome to Microsoft Sentinel Training Lab

<p align="center">
<img src="./Images/sentinel-labs-logo.png?raw=true">
</p>

## Introduction
These labs help you get ramped up with Microsoft Sentinel and provide hands-on practical experience for product features, capabilities, and scenarios. 

The lab deploys a Microsoft Sentinel workspace and ingests pre-recorded data to simulate scenarios that showcase various Microsoft Sentinel features. You should expect very little or no cost at all due to the size of the data (~10 MB), and the fact that Microsoft Sentinel offers a 30-day free trial on new workspaces.

## Prerequisites

Before you begin, make sure you have:

1. **Azure subscription** — If you don't have one, create a [free account](https://azure.microsoft.com/pricing/purchase-options/azure-account).
2. **Owner or Contributor role** on the target resource group (needed to create resources and assign RBAC roles during deployment).
3. **Microsoft Sentinel workspace onboarded to Microsoft Defender XDR** — The Log Analytics workspace must be connected to the [unified security operations platform (Defender XDR)](https://learn.microsoft.com/en-us/azure/sentinel/microsoft-sentinel-defender-portal) and set as the **primary workspace**. The [Onboarding exercise](./Exercises/Onboarding.md) walks you through this step by step.
4. **For the best experience**, enable [Microsoft Sentinel Data Lake](https://learn.microsoft.com/en-us/azure/sentinel/data-lake) on your workspace. This allows long-term, low-cost retention of security data and enables advanced hunting over extended time ranges.

## Custom Detection Rules Setup

This lab deploys **custom detection rules** to Microsoft Defender XDR via the Microsoft Graph Security API. The Automation runbook that creates the rules needs a **User-Assigned Managed Identity (UAMI)** with the `CustomDetection.ReadWrite.All` Microsoft Graph application permission.

> **Tip:** Leave the identity field empty during deployment if you want to skip custom detection rules entirely.

---

### Create a User-Assigned Managed Identity (UAMI)

> **Tip — Use GitHub Copilot:** You can complete this entire setup by pasting the following prompt into GitHub Copilot Chat in VS Code:
>
> *"Create a User-Assigned Managed Identity called SentinelDetectionRulesIdentity in my resource group, grant it the Microsoft Graph CustomDetection.ReadWrite.All application permission, and give me the full resource ID to use during deployment."*

#### 1. Create the UAMI

Open the [Azure portal](https://portal.azure.com/) and click the **Cloud Shell** button (>_) in the top navigation bar. Select **PowerShell** if prompted. Then replace `<your-resource-group>` with your resource group name and run:

```powershell
az identity create --resource-group <your-resource-group> --name SentinelDetectionRulesIdentity
```

#### 2. Grant the Microsoft Graph permission

In the same Cloud Shell session, replace `<your-resource-group>` and run each command:

```powershell
$miObjectId = (az identity show --resource-group <your-resource-group> --name SentinelDetectionRulesIdentity --query principalId -o tsv)
```

```powershell
$graphSpId = (az ad sp show --id "00000003-0000-0000-c000-000000000000" --query id -o tsv)
```

```powershell
$body = @{principalId=$miObjectId; resourceId=$graphSpId; appRoleId="e0fd9c8d-a12e-4cc9-9827-20c8c3cd6fb8"} | ConvertTo-Json -Compress
```

```powershell
az rest --method POST --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$graphSpId/appRoleAssignedTo" --headers "Content-Type=application/json" --body $body
```

#### 3. Deploy

Pass the UAMI's **full resource ID** as the `detectionRulesIdentityResourceId` parameter when deploying (in [Onboarding Step 4](./Exercises/Onboarding.md#step-4-deploy-the-microsoft-sentinel-training-lab-solution)):

```
/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/SentinelDetectionRulesIdentity
```

## Getting started

Start with the **Onboarding** exercise to set up your workspace and deploy the lab. Then work through the exercises in order.

### Exercise Dependencies

| Exercise | Prerequisites | Notes |
|---|---|---|
| **1–4** | None | Introductory — can be done in any order |
| **5** | MDE-onboarded device | Reference guide — hands-on requires MDE |
| **6–8** | None | Detection engineering (SIEM) |
| **9–10** | None | Operations (cost & table management) |
| **11** | Data lake enabled | Data lake KQL jobs |
| **12** | Exercise 11 | Builds on the KQL job output table |
| **14** | None | Independent — MCP server demo |
| **15** | ADLS Gen2 storage account | Data federation |
| **16** | Data lake enabled | Split transformation |

## Exercises

[**Onboarding — Setting up the environment**](./Exercises/Onboarding.md)
- Create a Log Analytics workspace and onboard Microsoft Sentinel
- Deploy the Training Lab solution

[**Exercise 1 — Exploration: Hunting Across Your Data**](./Exercises/E01_exploration.md)
- Discover tables, explore telemetry from CrowdStrike, Palo Alto, Okta, and AWS
- Create a custom detection rule for multi-tactic compromise

[**Exercise 2 — Threat Intelligence: Microsoft Defender Threat Intelligence**](./Exercises/E02_threat_intelligence_mdti.md)
- Enable the MDTI data connector and query the `ThreatIntelIndicators` table
- Match threat intelligence indicators against your environment's logs

[**Exercise 3 — MITRE ATT&CK Coverage**](./Exercises/E03_mitre_attack_coverage.md)
- View the MITRE ATT&CK coverage matrix for your deployed detection rules
- Identify coverage gaps and trace the lab's attack chain

[**Exercise 4 — Automation Rules**](./Exercises/E04_automation_rules.md)
- Create automation rules to tag incidents and escalate severity
- Understand rule ordering and condition logic

[**Exercise 5 — Cross-Platform Response Actions (Device Isolation)**](./Exercises/E05_device_isolation_response.md)
- (Optional) Isolate a device via MDE response actions triggered by CrowdStrike alerts

**--- SIEM Detection ---**

[**Exercise 6 — Port Scan Detection & Threshold Tuning**](./Exercises/E06_port_scan_threshold_tuning.md)
- Tune a detection rule's threshold and time window
- Explore KQL aggregation patterns for network reconnaissance

[**Exercise 7 — Okta MFA Factor Manipulation**](./Exercises/E07_okta_mfa_manipulation.md)
- Detect MFA factor deactivation events in Okta identity logs

[**Exercise 8 — Watchlist Integration**](./Exercises/E08_watchlist_integration.md)
- Create a watchlist and enrich detection rules with `_GetWatchlist()`

**--- Operations ---**

[**Exercise 9 — Cost Management & Ingestion Analysis**](./Exercises/E09_cost_management.md)
- Query the Usage table to analyse ingestion volume and cost drivers
- Explore cost optimisation strategies and the Workspace Usage Report

[**Exercise 10 — Table Management: Tiers & Retention**](./Exercises/E10_table_management.md)
- Configure table tiers (Analytics vs Data Lake) and retention periods
- Understand the cost and capability trade-offs

**--- Data Lake ---**

[**Exercise 11 — Data Lake KQL Jobs**](./Exercises/E11_datalake_kql_jobs.md)
- Create and schedule KQL jobs to aggregate data lake telemetry
- Promote summarised data for detection rules

[**Exercise 12 — Data Lake vs Real-Time Detection**](./Exercises/E12_datalake_port_diversity.md)
- Compare real-time and data lake detection approaches
- Build a detection against pre-aggregated data

[**Exercise 13 — Data Lake Notebooks**](./Exercises/E13_notebooks.md)
- Interactive Jupyter notebook investigation using PySpark

**--- Tools ---**

[**Exercise 14 — Sentinel MCP Server Demo Prompts**](./Exercises/E14_MCP.md)
- 10 AI assistant prompts demonstrating Sentinel MCP Server capabilities

[**Exercise 15 — Data Federation with ADLS Gen2**](./Exercises/E15_federation_adls.md)
- Federate external data from Azure Data Lake Storage Gen2
- Query security events alongside Sentinel tables without ingestion

[**Exercise 16 — Data Transformation: Split Ingestion by Tier**](./Exercises/E16_split_transformation.md)
- Create a split transformation to route firewall data between Analytics and Data lake tiers
- Understand cost optimisation through tiered ingestion

---

## Reference

> **Optional — Exercise 5 (Device Isolation Response):** This exercise requires a machine onboarded to **Microsoft Defender for Endpoint (MDE)**. If you plan to complete Exercise 5, onboard a test device to MDE before starting. See [Onboard devices to Microsoft Defender for Endpoint](https://learn.microsoft.com/en-us/defender-endpoint/onboarding) for instructions.

### Release notes

* Version 1.0 - Microsoft Sentinel Training Lab
