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

This lab deploys **custom detection rules** to Microsoft Defender XDR via the Microsoft Graph Security API. The Automation runbook that creates the rules needs an identity with the `CustomDetection.ReadWrite.All` Microsoft Graph application permission. You can use **either** a User-Assigned Managed Identity (UAMI) **or** a Service Principal (App Registration) — pick the option that suits your environment.

> **Tip:** Leave all identity fields empty during deployment if you want to skip custom detection rules entirely.

Complete **one** of the two options below before deployment.

---

### Option A — User-Assigned Managed Identity (UAMI)

#### A1. Create the UAMI

```powershell
# Create the UAMI (adjust resource group and name as needed)
az identity create `
  --resource-group <your-resource-group> `
  --name SentinelDetectionRulesIdentity
```

#### A2. Grant the Microsoft Graph permission

```powershell
# Variables
$miObjectId   = (az identity show --resource-group <your-resource-group> --name SentinelDetectionRulesIdentity --query principalId -o tsv)
$graphAppId   = "00000003-0000-0000-c000-000000000000"   # Microsoft Graph
$appRoleId    = "e0fd9c8d-a12e-4cc9-9827-20c8c3cd6fb8"   # CustomDetection.ReadWrite.All

# Get the Microsoft Graph service principal
$graphSpId = (az ad sp show --id $graphAppId --query id -o tsv)

# Assign the app role to the managed identity
az rest --method POST `
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$graphSpId/appRoleAssignedTo" `
  --headers "Content-Type=application/json" `
  --body "{\"principalId\":\"$miObjectId\",\"resourceId\":\"$graphSpId\",\"appRoleId\":\"$appRoleId\"}"
```

#### A3. Deploy

Pass the UAMI's **full resource ID** as the `detectionRulesIdentityResourceId` parameter when deploying (in [Onboarding Exercise 8](./Exercises/Onboarding.md#exercise-8-deploy-the-microsoft-sentinel-training-lab-solution)):

```
/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/SentinelDetectionRulesIdentity
```

---

### Option B — Service Principal (App Registration)

Use this option when you cannot create or use a Managed Identity (e.g., cross-tenant deployments or restricted RBAC environments).

**Prefer the portal?** You can complete steps B1–B3 entirely from the Azure portal by following [Create a Microsoft Entra app and service principal in the portal](https://learn.microsoft.com/entra/identity-platform/howto-create-service-principal-portal). That guide covers app registration, API permission assignment (use **Microsoft Graph → Application permissions → CustomDetection.ReadWrite.All**), and client secret creation. Once done, skip ahead to **B4** below.

<p align="center">
<img src="./Images/OnboardingImage8.png?raw=true">
</p>

#### B1. Create an App Registration

```powershell
# Create the app registration
az ad app create --display-name SentinelDetectionRulesSPN

# Note the appId (client ID) from the output
$appId = (az ad app list --display-name SentinelDetectionRulesSPN --query "[0].appId" -o tsv)

# Create a service principal for the app
az ad sp create --id $appId
```

#### B2. Grant the Microsoft Graph permission

```powershell
$spObjectId   = (az ad sp show --id $appId --query id -o tsv)
$graphAppId   = "00000003-0000-0000-c000-000000000000"   # Microsoft Graph
$appRoleId    = "e0fd9c8d-a12e-4cc9-9827-20c8c3cd6fb8"   # CustomDetection.ReadWrite.All

$graphSpId = (az ad sp show --id $graphAppId --query id -o tsv)

az rest --method POST `
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$graphSpId/appRoleAssignedTo" `
  --headers "Content-Type=application/json" `
  --body "{\"principalId\":\"$spObjectId\",\"resourceId\":\"$graphSpId\",\"appRoleId\":\"$appRoleId\"}"
```

> **Note:** Granting application permissions requires **Global Administrator** or **Privileged Role Administrator** in Microsoft Entra ID, or admin consent must be granted afterwards.

#### B3. Create a client secret

```powershell
az ad app credential reset --id $appId --append
# Save the "password" value — it will not be shown again.
```

#### B4. Deploy

During deployment, provide the following three parameters (leave the UAMI field empty):

| Parameter | Value |
|---|---|
| `detectionRulesSpnTenantId` | Your Microsoft Entra **Tenant ID** |
| `detectionRulesSpnClientId` | The **Application (client) ID** from step B1 |
| `detectionRulesSpnClientSecret` | The **client secret** from step B3 |

## Getting started

Start with the **Onboarding** exercise to set up your workspace, install solutions, and deploy the lab. Then work through the exercises in order. Exercises 1–4 are introductory and can be done in any order. Exercise 5 is optional (requires MDE). Exercises 6–7 cover cost and table management. Exercises 8–10 cover detection engineering and data lake topics (do 9 before 10). Exercises 11–12 are detection-focused. Exercises 13–14 are independent demos.

## Exercises

[**Onboarding — Setting up the environment**](./Exercises/Onboarding.md)
- Create a Log Analytics workspace and onboard Microsoft Sentinel
- Install Content Hub solutions and set up data connectors
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

---

## Reference

> **Optional — Exercise 5 (Device Isolation Response):** This exercise requires a machine onboarded to **Microsoft Defender for Endpoint (MDE)**. If you plan to complete Exercise 5, onboard a test device to MDE before starting. See [Onboard devices to Microsoft Defender for Endpoint](https://learn.microsoft.com/en-us/defender-endpoint/onboarding) for instructions.

### Release notes

* Version 1.0 - Microsoft Sentinel Training Lab
