# Check Point Exposure Management Alerts - Microsoft Sentinel Solution

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/checkpoint.svg" width="75px" height="75px">

## Overview

This solution integrates **Check Point Exposure Management** with **Microsoft Sentinel** and keeps alert status in sync in both directions. Argos alerts become Microsoft Sentinel incidents, status changes made in either system are mirrored to the other, and SOC teams can enrich and respond to alerts from Microsoft Sentinel.

### What's Included

| Component | Description |
|-----------|-------------|
| **Data Connector** (CCP) | Polls the Argos Alerts API every 5 minutes for alerts created or changed in that window |
| **2 Analytic Rules** | Creates an incident per Argos alert; detects ingestion gaps |
| **9 Playbook templates** | Status sync in both directions, enrichment, response, and the automation rule that wires outbound sync |
| **1 Parser** | `CPEMAlerts`: latest state of each alert with category metadata |
| **1 Workbook** | Alert overview, status distribution, and sync health monitoring |

## Architecture

```
            ┌──────────────────────────────────────┐
            │  Check Point Exposure Management     │
            │  (Argos Alerts API)                  │
            └───────┬──────────────────────▲───────┘
                    │ POST /alerts          │ GET /alerts/{ref_id}
                    │ (update_date window)  │ PUT /alerts/status
                    ▼                       │
          ┌───────────────────┐   ┌─────────┴──────────┐
          │ CCP data connector│   │ Exporter           │
          └─────────┬─────────┘   │ (Sentinel → Argos) │
                    ▼             └─────────▲──────────┘
          ┌───────────────────┐             │ Automation rule:
          │ argsentdc_CL      │             │ status changed
          │ one row per change│             │
          └──┬─────────────┬──┘   ┌─────────┴──────────┐
             │             │      │ Microsoft Sentinel │
   first seen│             │later │ incidents          │
             ▼             ▼      └──▲──────────────▲──┘
  ┌────────────────┐ ┌──────────────┴────┐          │
  │ Analytic rule  │ │ InboundStatusSync │          │
  │ Argos alerts   │ │ (Argos → Sentinel)│          │
  │ to incidents   ├─┼───────────────────┼──────────┘
  └────────────────┘ └───────────────────┘  creates incident + alert
                                            with ref_id Custom Detail
```

**How the sync works:**
- **Ingestion.** The CCP connector filters on `update_date`, so every change to an Argos alert (new, acknowledged, closed, reopened) adds a row to `argsentdc_CL`. The latest row per `ref_id` is the current Argos state.
- **Incident creation.** The **Argos alerts to incidents** rule creates one incident the first time an alert appears as `open` or `acknowledged`, with `ref_id` as a Custom Detail. Later rows for the same alert never create another incident.
- **Argos → Microsoft Sentinel.** **Check_Point_EM_InboundStatusSync** runs every 5 minutes, compares the latest Argos state with the incident, and updates the incident status and classification when they differ.
- **Microsoft Sentinel → Argos.** The automation rule runs **Check_Point_EM_Exporter** whenever an incident's status changes. The Exporter updates the Argos alert through `PUT /alert/api/v1/alerts/status`.
- **Conflicts.** The newest change wins. InboundStatusSync only overwrites an incident whose last status change is older than the Argos change.
- **Loop prevention.** The Exporter reads the Argos alert first and sends nothing when Argos already has the target state, so a change applied by InboundStatusSync is not echoed back.

## Prerequisites

1. **Microsoft Sentinel** enabled on a Log Analytics workspace.
2. A **Check Point Exposure Management API token** and your tenant URL (for example `https://your_tenant.cyberint.io`). The connector and every playbook take this same URL; the service path (`/alert`, `/takedown`) is added automatically.
3. **Owner** or **User Access Administrator** on the resource group, to grant the playbooks' managed identities their role.

## Deployment

### Step 1: Install the solution from Content Hub

1. In the Azure portal, go to **Microsoft Sentinel > Content hub**.
2. Search for **Check Point Cyberint Alerts** and click **Install**.

### Step 2: Connect the data connector

Open **Data connectors > Check Point Cyberint Alerts Connector (via Codeless Connector Platform)**, enter the tenant URL, API token and customer name, and click **Connect**.

### Step 3: Create the analytic rules

In **Analytics > Rule templates**, create rules from:
- **Check Point Exposure Management - Argos alerts to incidents** (required for sync)
- **Check Point Exposure Management - Alert Ingestion Anomaly** (recommended)

### Step 4: Create the sync playbooks

Create them from **Automation > Playbook templates**, or deploy the standalone templates:

| Playbook | Deploy | Required parameters |
|----------|--------|---------------------|
| **Check_Point_EM_Exporter** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_OutboundSync%2Fazuredeploy.json) | `API_Base_URL`, `API_Access_Token` |
| **Check_Point_EM_InboundStatusSync** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_InboundStatusSync%2Fazuredeploy.json) | `Workspace_Name` |
| **Check_Point_EM_ManualStatusUpdate** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_ManualStatusUpdate%2Fazuredeploy.json) | `API_Base_URL`, `API_Access_Token` |
| **Check_Point_EM_AutomationRules** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_AutomationRules%2Fazuredeploy.json) | `Sentinel_Workspace_Resource_Id` (deploy after the Exporter) |

Get the workspace resource ID with:

```bash
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --query id -o tsv
```

### Step 5: Enrichment and response playbooks (optional)

| Playbook | Deploy | Description |
|----------|--------|-------------|
| **Check_Point_EM_FetchAttachments** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FEnrichment%2FCPEM_FetchAttachments%2Fazuredeploy.json) | Adds alert attachments and the analysis report to the incident |
| **Check_Point_EM_IOCEnrichment** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FEnrichment%2FCPEM_IOCEnrichment%2Fazuredeploy.json) | Enriches incident IOCs (IPs, domains, hashes, URLs) |
| **Check_Point_EM_CredentialLeakResponse** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FResponse%2FCPEM_CredentialLeakResponse%2Fazuredeploy.json) | Validates leaked credentials |
| **Check_Point_EM_VulnerabilityMonitoring** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FResponse%2FCPEM_VulnerabilityMonitoring%2Fazuredeploy.json) | Enriches CVE and vulnerability alerts |
| **Check_Point_EM_PhishingTakedown** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FResponse%2FCPEM_PhishingTakedown%2Fazuredeploy.json) | Requests a phishing site takedown |

### Step 6: Grant the managed identities their role

Every playbook that reads or updates incidents needs **Microsoft Sentinel Responder** on the workspace resource group. For InboundStatusSync this one role also covers the log query.

```bash
for PB in Check_Point_EM_Exporter Check_Point_EM_InboundStatusSync Check_Point_EM_ManualStatusUpdate; do
  PRINCIPAL_ID=$(az logic workflow show --resource-group <rg-name> --name $PB --query identity.principalId -o tsv)
  az role assignment create \
    --assignee-object-id $PRINCIPAL_ID \
    --assignee-principal-type ServicePrincipal \
    --role "Microsoft Sentinel Responder" \
    --scope "/subscriptions/<sub-id>/resourceGroups/<rg-name>"
done
```

Add any enrichment or response playbooks you deployed to the list.

### Upgrading from 3.1.x

Content Hub updates templates, not the resources already created from them:

1. **Disconnect and reconnect the data connector.** A connector connected under 3.1.x keeps filtering on `created_date` and never sees status changes.
2. **Recreate the Exporter, ManualStatusUpdate and AutomationRules playbooks** from their updated templates, and create **InboundStatusSync**.
3. **Disable or delete the `Check_Point_EM_Importer` Logic App**, its API connections and its data collection endpoint. It is no longer part of the solution, and left running it creates incidents with no alerts, which can never sync.
4. **Review custom queries on `argsentdc_CL`.** The table now holds one row per alert change; use `summarize arg_max(TimeGenerated, *) by ref_id` or the `CPEMAlerts` parser for the current state.

### Verify data flow

```kql
argsentdc_CL
| summarize rows = count(), alerts = dcount(ref_id) by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
| take 24
```

Then open the **Check Point Exposure Management - Alert Overview** workbook.

## Playbook Reference

### Status sync

| Playbook | Trigger | Direction | Description |
|----------|---------|-----------|-------------|
| **Check_Point_EM_InboundStatusSync** | Recurrence (5 min) | Argos → Microsoft Sentinel | Applies Argos status changes to incidents |
| **Check_Point_EM_Exporter** | Automation rule | Microsoft Sentinel → Argos | Pushes incident status changes to Argos |
| **Check_Point_EM_ManualStatusUpdate** | Manual | Microsoft Sentinel → Argos | Pushes the current incident status on demand |
| **Check_Point_EM_AutomationRules** | — | — | Automation rule that runs the Exporter on every status change |

### Enrichment and response

| Playbook | Trigger | Description |
|----------|---------|-------------|
| **Check_Point_EM_FetchAttachments** | Manual | Fetches alert attachments and analysis reports |
| **Check_Point_EM_IOCEnrichment** | Automation rule | Enriches IPs, domains, hashes, URLs via Check Point threat intel |
| **Check_Point_EM_CredentialLeakResponse** | Manual/Automation | Validates leaked credential alerts |
| **Check_Point_EM_VulnerabilityMonitoring** | Manual/Automation | Enriches CVE and vulnerability alerts |
| **Check_Point_EM_PhishingTakedown** | Manual/Automation | Requests phishing site takedown |

## Status Mapping

### Microsoft Sentinel → Argos (Exporter, ManualStatusUpdate)

| Microsoft Sentinel status | Classification / reason | Argos status | Argos closure reason |
|---|---|---|---|
| New | — | `open` | — |
| Active | — | `acknowledged` | — |
| Closed | True Positive | `closed` | `resolved` |
| Closed | Benign Positive | `closed` | `no_longer_a_threat` |
| Closed | False Positive / Incorrect alert logic | `closed` | `false_positive` |
| Closed | False Positive / Inaccurate data | `closed` | `irrelevant_alert_subtype` |
| Closed | Undetermined | `closed` | `other`, with the classification comment as the description (`undetermined` when empty) |

### Argos → Microsoft Sentinel (InboundStatusSync)

| Argos status | Argos closure reason | Microsoft Sentinel status | Classification / reason |
|---|---|---|---|
| `open` | — | New | — |
| `acknowledged` | — | Active | — |
| `closed` | `resolved` | Closed | True Positive / Suspicious activity |
| `closed` | `false_positive` | Closed | False Positive / Incorrect alert logic |
| `closed` | `irrelevant_alert_subtype` | Closed | False Positive / Inaccurate data |
| `closed` | `no_longer_a_threat`, `irrelevant`, `asset_should_not_be_monitored`, `asset_belongs_to_my_organization`, `asm_no_longer_detected`, `asm_manually_closed` | Closed | Benign Positive / Suspicious but expected |
| `closed` | `other` or none | Closed | Undetermined |

On close, the Argos closure reason description (or the closure reason itself when there is no description) becomes the classification comment.

## Known Limitations

- **Only an alert's latest change is visible.** The Argos API filters on an alert's current `update_date`, so the connector sees the state an alert is in when it polls, not every intermediate change. If another integration or script rewrites the same alerts more often than the connector polls (every 5 minutes), each poll can find nothing new and changes are missed until the rewriting stops.
- **The Argos API quota is shared per token.** Argos allows 5,000 requests per 24 hours (and 60 per minute) per API token. The connector uses about 288 requests a day, and each Exporter run makes one read and at most one write per Argos alert. Other integrations using the same token draw from the same quota; when it runs out, polling and status sync stop until requests age out of the 24-hour window. Use a dedicated token for this solution.
- **Incidents are only created for alerts first seen within 47 hours of creation.** This is the longest lookback Microsoft Sentinel allows for a rule that runs every 5 minutes.
- **Only status is mirrored.** Changing the closure reason of an alert that is already closed on both sides is not re-synced.
- **Sync latency is about 10–15 minutes** in each direction from Argos: one connector poll plus one InboundStatusSync run. Microsoft Sentinel changes reach Argos within about a minute.

## Troubleshooting

### No data in argsentdc_CL

1. Verify the CCP data connector is connected in **Data connectors**.
2. Check the API token hasn't expired.
3. Ensure the tenant URL is correct and reachable from Azure.

### Argos changes don't reach Microsoft Sentinel

1. Confirm the connector was connected under 3.2.0 or later: its request must filter on `update_date`. Reconnect it otherwise.
2. Check the **Check_Point_EM_InboundStatusSync** run history. A 403 on `Find_incidents_out_of_sync` or `Get_incident` means the managed identity lacks **Microsoft Sentinel Responder**.
3. The incident must have been created by the **Argos alerts to incidents** rule; incidents without the `ref_id` Custom Detail cannot be matched.

### Microsoft Sentinel changes don't reach Argos

1. Verify the **Check Point EM - Sync incident status to Argos on status change** automation rule is enabled in **Automation**.
2. Check the Exporter run history and the comment it adds to the incident. `already <status> in Argos, no update sent` means Argos already matched; an HTTP code other than 200 means the Argos call failed.
3. Confirm the Exporter's managed identity has **Microsoft Sentinel Responder**.

## Data Schema

The `argsentdc_CL` custom table contains these key columns:

| Column | Type | Description |
|--------|------|-------------|
| `ref_id` | string | Unique alert reference ID |
| `event_title` | string | Alert title (renamed from `title`) |
| `event_type` | string | Alert type (renamed from `type`) |
| `status` | string | Alert status (`open`, `acknowledged`, `closed`) |
| `severity` | string | Severity level (`low`, `medium`, `high`, `very_high`) |
| `category` | string | Alert category |
| `created_date` | datetime | When the alert was created |
| `modification_date` | datetime | When the alert was last modified |
| `TimeGenerated` | datetime | The alert's `update_date`: when this change happened in Argos |
| `closure_reason` | dynamic | Closure reason (if closed) |
| `closure_reason_description` | dynamic | Closure reason description (if any) |
| `threat_actor` | string | Attributed threat actor (if any) |
| `iocs` | dynamic | Associated indicators of compromise |
| `mitre` | dynamic | MITRE ATT&CK mapping |

## Support

- **Provider:** Check Point
- **Tier:** Partner
- **Contact:** [Check Point Support](https://www.checkpoint.com/support-services/contact-support/)

## Maintainers' notes

- **`offerId`:** `checkpoint-cyberint-solutions-alerts`. This identifier does not include the `azure-sentinel-` prefix used by the sibling Cyberint solutions (`azure-sentinel-checkpoint-cyberint-ioc`, `azure-sentinel-checkpoint-em-threatcloud-intelligence-feed`). The Alerts solution was first published on 2025-03-18 under the existing `offerId` and versions 3.0.0 / 3.0.1 / 3.1.0 are already live in the marketplace. Renaming would orphan the published offer and break the upgrade path for existing customers, so the historical identifier is preserved deliberately. New solutions in the Cyberint family should follow the `azure-sentinel-…` convention.
