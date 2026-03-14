# Check Point Exposure Management Alerts - Microsoft Sentinel Solution

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/checkpoint-cyberint.svg" width="75px" height="75px">

## Overview

This solution integrates **Check Point Exposure Management** with **Microsoft Sentinel**, providing bi-directional synchronization of alerts and incidents. It enables SOC teams to manage Argos external risk alerts directly from Sentinel while keeping both platforms in sync.

### What's Included

| Component | Description |
|-----------|-------------|
| **Data Connector** (CCP) | Ingests new alerts every 5 minutes via the Codeless Connector Platform |
| **10 Playbooks** | Bi-directional sync, enrichment, and response automation |
| **1 Analytic Rule** | Detects ingestion gaps (connector or sync failures) |
| **1 Workbook** | Alert overview, status distribution, and sync health monitoring |
| **1 Automation Rule** | Triggers outbound sync on incident updates |

## Architecture

```
                    ┌──────────────────────┐
                    │   Check Point Exposure Management      │
                    │   (External Risk Mgmt)│
                    └──────┬───────▲───────┘
                           │       │
              ┌────────────┘       └────────────┐
              │ (new alerts)        (status PUT) │
              ▼                                  │
    ┌─────────────────┐              ┌───────────┴───────┐
    │ CCP Data        │              │ Exporter     │
    │ Connector       │              │ Playbook          │
    │ (created_date)  │              │ (Sentinel → Argos)│
    └────────┬────────┘              └───────────▲───────┘
             │                                   │
             ▼                                   │
    ┌─────────────────┐              ┌───────────┴───────┐
    │ argsentdc_CL    │◄─────────────│ Importer      │
    │ (Custom Table)  │              │ Playbook           │
    └────────┬────────┘              │ (modification_date)│
             │                       └───────────────────┘
             ▼
    ┌─────────────────┐
    │ Microsoft        │
    │ Sentinel         │
    │ (Incidents)      │
    └──────────────────┘
```

**Two ingestion paths:**
- **CCP Connector** — polls for **new** alerts using `created_date` filter (every 5 min)
- **Importer** — polls for **modified** alerts using `modification_date` filter (every 10 min)

**Loop prevention:** Importer tags incidents with `argos-importer-synced`. Exporter checks for this tag and skips if present, preventing circular updates.

## Prerequisites

1. **Microsoft Sentinel** enabled on a Log Analytics workspace.
2. A **Check Point Exposure Management API token** and your environment's **Check Point Exposure Management API base URL** (e.g., `https://app.cyberint.io`).
3. **Contributor** role on the target resource group (for deploying Logic Apps, Key Vault, and role assignments).
4. The CCP data connector's **Data Collection Endpoint (DCE)** URL and **Data Collection Rule (DCR) immutable ID** (required for Importer).

## Deployment

### Recommended Deployment Order

Deploy components in this sequence to satisfy dependencies:

#### Step 1: Install the Solution from Content Hub

1. In the Azure portal, go to **Microsoft Sentinel > Content Hub**.
2. Search for **Check Point Exposure Management Alerts**.
3. Click **Install** to deploy the data connector, analytic rule template, and workbook.
4. Configure the CCP data connector with your Check Point Exposure Management API URL and token.

#### Step 2: Deploy Base Infrastructure

Deploy **Check_Point_EM_Base** first — all other playbooks depend on it.

[![Deploy Check_Point_EM_Base](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_Base%2Fazuredeploy.json)

Provide your **Check Point Exposure Management API token** and **base URL**. The template creates a Key Vault, stores the token, and sets up Managed Identity access automatically.

#### Step 3: Deploy Sync Playbooks

Deploy in any order. All require `Check_Point_EM_Base` to be deployed first.

| Playbook | Deploy | Required Parameters |
|----------|--------|-------------------|
| **Importer** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_Importer%2Fazuredeploy.json) | DCE URL, DCR immutable ID |
| **Exporter** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_Exporter%2Fazuredeploy.json) | — |
| **Manual Status Update** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_ManualStatusUpdate%2Fazuredeploy.json) | — |
| **Fetch Attachments** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_FetchAttachments%2Fazuredeploy.json) | — |

#### Step 4: Deploy XDR/SOAR Playbooks (Optional)

| Playbook | Deploy | Description |
|----------|--------|-------------|
| **IOC Enrichment** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_IOCEnrichment%2Fazuredeploy.json) | Enrich incident IOCs (IPs, domains, hashes, URLs) |
| **Credential Leak Response** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_CredentialLeakResponse%2Fazuredeploy.json) | Validate leaked credentials |
| **Vulnerability Monitoring** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_VulnerabilityMonitoring%2Fazuredeploy.json) | Enrich CVE/vulnerability alerts |
| **Phishing Takedown** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_PhishingTakedown%2Fazuredeploy.json) | Request phishing site takedown |

#### Step 5: Deploy Automation Rule

Deploy after Exporter to wire the automation trigger.

[![Deploy Automation Rules](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_AutomationRules%2Fazuredeploy.json)

Get your Sentinel workspace resource ID:

```bash
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --query id -o tsv
```

## Post-Deployment Configuration

### 1. Grant Managed Identity Roles

Playbooks that interact with Sentinel incidents need the **Microsoft Sentinel Responder** role:

```bash
# Get the Logic App's Managed Identity principal ID
PRINCIPAL_ID=$(az logic workflow show \
  --resource-group <rg-name> \
  --name Check_Point_EM_Exporter \
  --query identity.principalId -o tsv)

# Assign Sentinel Responder role
az role assignment create \
  --assignee-object-id $PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --role "Microsoft Sentinel Responder" \
  --scope "/subscriptions/<sub-id>/resourceGroups/<rg-name>"
```

Repeat for: `Check_Point_EM_Exporter`, `Check_Point_EM_ManualStatusUpdate`, `Check_Point_EM_FetchAttachments`, and any XDR/SOAR playbooks.

### 2. Enable the Analytic Rule

1. Go to **Microsoft Sentinel > Analytics**.
2. Find **Check Point Exposure Management - Alert Ingestion Anomaly** in the rule templates.
3. Click **Create rule** to enable it.

### 3. Verify Data Flow

1. Check the CCP connector status in **Data Connectors**.
2. Run this KQL query to verify data is flowing:

```kql
argsentdc_CL
| summarize count() by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
| take 24
```

3. Open the **Check Point Exposure Management - Alert Overview & Sync Health** workbook to verify the dashboard.

## Playbook Reference

### Bi-Directional Sync

| Playbook | Trigger | Direction | Description |
|----------|---------|-----------|-------------|
| **Check_Point_EM_Importer** | Recurrence (10 min) | Argos → Sentinel | Polls for modified alerts, writes to `argsentdc_CL` |
| **Check_Point_EM_Exporter** | Automation Rule | Sentinel → Argos | Pushes incident status changes to Argos |
| **Check_Point_EM_ManualStatusUpdate** | Manual | Sentinel → Argos | On-demand status push from incident |
| **Check_Point_EM_FetchAttachments** | Manual | Argos → Sentinel | Fetches alert attachments and analysis reports |

### XDR/SOAR

| Playbook | Trigger | Description |
|----------|---------|-------------|
| **Check_Point_EM_IOCEnrichment** | Automation Rule | Enriches IPs, domains, hashes, URLs via Check Point threat intel |
| **Check_Point_EM_CredentialLeakResponse** | Manual/Automation | Validates leaked credential alerts |
| **Check_Point_EM_VulnerabilityMonitoring** | Manual/Automation | Enriches CVE and vulnerability alerts |
| **Check_Point_EM_PhishingTakedown** | Manual/Automation | Requests phishing site takedown |

### Infrastructure

| Component | Description |
|-----------|-------------|
| **Check_Point_EM_Base** | Key Vault + Managed Identity + token retrieval |
| **Check_Point_EM_AutomationRules** | Automation rule wiring for Exporter |

## Status Mapping (Bi-Directional)

| Sentinel Status | Sentinel Classification | Argos Status | Argos Closure Reason |
|----------------|------------------------|--------------|---------------------|
| Active | — | `open` | — |
| Closed | True Positive | `closed` | `true_positive` |
| Closed | False Positive | `closed` | `false_positive` |
| Closed | Benign Positive | `closed` | `benign_positive` |
| Closed | Undetermined | `closed` | `undetermined` |

## Troubleshooting

### No data in argsentdc_CL

1. Verify the CCP data connector is connected in **Data Connectors**.
2. Check the API token hasn't expired.
3. Ensure the Check Point Exposure Management API URL is correct and accessible from Azure.

### Importer not writing records

1. Check the Logic App run history for errors.
2. Verify the DCE URL and DCR immutable ID parameters are correct.
3. Confirm the Managed Identity has the **Monitoring Metrics Publisher** role.

### Exporter not firing

1. Verify the automation rule is enabled in **Sentinel > Automation**.
2. Check the Logic App run history — look for runs that were skipped (loop prevention or no status change).
3. Confirm the Managed Identity has **Microsoft Sentinel Responder** role.

### Loop prevention blocking legitimate syncs

The `argos-importer-synced` tag is set by Importer. If you need to manually trigger an outbound sync after an inbound update, use the **Manual Status Update** playbook (it bypasses loop prevention).

## Data Schema

The `argsentdc_CL` custom table contains these key columns:

| Column | Type | Description |
|--------|------|-------------|
| `ref_id` | datetime | Unique alert reference ID |
| `event_title` | string | Alert title (renamed from `title`) |
| `event_type` | string | Alert type (renamed from `type`) |
| `status` | string | Alert status (`open`, `closed`) |
| `severity` | string | Severity level (`low`, `medium`, `high`, `very_high`) |
| `category` | string | Alert category |
| `created_date` | datetime | When the alert was created |
| `modification_date` | datetime | When the alert was last modified |
| `TimeGenerated` | datetime | Ingestion timestamp (mapped from `update_date`) |
| `closure_reason` | dynamic | Closure reason (if closed) |
| `threat_actor` | string | Attributed threat actor (if any) |
| `iocs` | dynamic | Associated indicators of compromise |
| `mitre` | dynamic | MITRE ATT&CK mapping |

## Support

- **Provider:** Check Point
- **Tier:** Partner
- **Contact:** [Check Point Support](https://cyberint.com/customer-support/)
