# Check Point Exposure Management Alerts - Microsoft Sentinel Solution

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/checkpoint.svg" width="75px" height="75px">

## Overview

This solution integrates **Check Point Exposure Management** with **Microsoft Sentinel**. Argos alerts become Microsoft Sentinel incidents, and status changes made in Argos are mirrored onto those incidents.

> **Microsoft Sentinel → Argos sync is not available in this version.** The Argos API accepts its token only as a cookie, and Azure Logic Apps removes the `Cookie` header from outgoing requests, so no playbook can authenticate to Argos. See [Known Limitations](#known-limitations).

### What's Included

| Component | Description |
|-----------|-------------|
| **Data Connector** (CCP) | Polls the Argos Alerts API every 5 minutes for alerts created or changed in that window |
| **2 Analytic Rules** | Creates an incident per Argos alert; detects ingestion gaps |
| **6 Playbook templates** | Inbound status sync, enrichment and response |
| **1 Parser** | `CPEMAlerts`: latest state of each alert with category metadata |
| **1 Workbook** | Alert overview, status distribution, and sync health monitoring |

## Architecture

```
            ┌──────────────────────────────────────┐
            │  Check Point Exposure Management     │
            │  (Argos Alerts API)                  │
            └───────┬──────────────────────────────┘
                    │ POST /alerts (update_date window)
                    ▼
          ┌───────────────────┐
          │ CCP data connector│
          └─────────┬─────────┘
                    ▼
          ┌───────────────────┐
          │ argsentdc_CL      │
          │ one row per change│
          └──┬─────────────┬──┘
             │             │
   first seen│             │later changes
             ▼             ▼
  ┌────────────────┐ ┌───────────────────┐
  │ Analytic rule  │ │ InboundStatusSync │
  │ Argos alerts   │ │ (Argos → Sentinel)│
  │ to incidents   │ └─────────┬─────────┘
  └────────┬───────┘           │
           ▼                   ▼
      ┌────────────────────────────┐
      │ Microsoft Sentinel         │
      │ incidents (ref_id Custom   │
      │ Detail)                    │
      └────────────────────────────┘
```

**How the sync works:**
- **Ingestion.** The CCP connector filters on `update_date`, so every change to an Argos alert (new, acknowledged, closed, reopened) adds a row to `argsentdc_CL`. The latest row per `ref_id` is the current Argos state.
- **Incident creation.** The **Argos alerts to incidents** rule creates one incident the first time an alert appears as `open` or `acknowledged`, with `ref_id` as a Custom Detail.
- **Argos → Microsoft Sentinel.** **Check_Point_EM_InboundStatusSync** runs every 5 minutes, compares the latest Argos state with the incident, and updates the incident status and classification when they differ. It runs entirely inside Azure and needs no Argos credentials.
- **Microsoft Sentinel → Argos.** Not available; see [Known Limitations](#known-limitations).

## Prerequisites

1. **Microsoft Sentinel** enabled on a Log Analytics workspace.
2. A **Check Point Exposure Management API token** and your tenant URL (for example `https://your_tenant.cyberint.io`), for the data connector.
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

### Step 4: Create the inbound status sync playbook

Create it from **Automation > Playbook templates**, or deploy the standalone template:

| Playbook | Deploy | Required parameters |
|----------|--------|---------------------|
| **Check_Point_EM_InboundStatusSync** | [![Deploy](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_InboundStatusSync%2Fazuredeploy.json) | `Workspace_Name` |

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
for PB in Check_Point_EM_InboundStatusSync; do
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
2. **Create the `Check_Point_EM_InboundStatusSync` playbook** and grant it **Microsoft Sentinel Responder**.
3. **Stop the outbound sync.** The `Check_Point_EM_Exporter` and `Check_Point_EM_ManualStatusUpdate` playbooks are no longer shipped, and any existing copies cannot authenticate to Argos (see Known Limitations). Disable the automation rule that runs the Exporter so it stops producing failed runs and misleading incident comments.
4. **Disable or delete the `Check_Point_EM_Importer` Logic App**, its API connections and its data collection endpoint. It is no longer part of the solution, and left running it creates incidents with no alerts, which can never sync.
5. **Review custom queries on `argsentdc_CL`.** The table now holds one row per alert change; use `summarize arg_max(TimeGenerated, *) by ref_id` or the `CPEMAlerts` parser for the current state.

### Verify data flow

```kql
argsentdc_CL
| summarize rows = count(), alerts = dcount(ref_id) by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
| take 24
```

Then open the **Check Point Exposure Management - Alert Overview** workbook.

## Playbook Reference

| Playbook | Trigger | Description |
|----------|---------|-------------|
| **Check_Point_EM_InboundStatusSync** | Recurrence (5 min) | Applies Argos status changes to the matching incidents. Needs no Argos credentials |
| **Check_Point_EM_FetchAttachments** | Manual | Fetches alert attachments and analysis reports |
| **Check_Point_EM_IOCEnrichment** | Automation rule | Enriches IPs, domains, hashes, URLs via Check Point threat intel |
| **Check_Point_EM_CredentialLeakResponse** | Manual/Automation | Validates leaked credential alerts |
| **Check_Point_EM_VulnerabilityMonitoring** | Manual/Automation | Enriches CVE and vulnerability alerts |
| **Check_Point_EM_PhishingTakedown** | Manual/Automation | Requests phishing site takedown |

Every playbook except InboundStatusSync calls the Argos API and is therefore affected by the authentication limitation below.

## Status Mapping (Argos → Microsoft Sentinel)

| Argos status | Argos closure reason | Microsoft Sentinel status | Classification / reason |
|---|---|---|---|
| `open` | — | New | — |
| `acknowledged` | — | Active | — |
| `closed` | `resolved` | Closed | True Positive / Suspicious activity |
| `closed` | `false_positive` | Closed | False Positive / Incorrect alert logic |
| `closed` | `irrelevant_alert_subtype` | Closed | False Positive / Inaccurate data |
| `closed` | `no_longer_a_threat`, `irrelevant`, `asset_should_not_be_monitored`, `asset_belongs_to_my_organization`, `asm_no_longer_detected`, `asm_manually_closed` | Closed | Benign Positive / Suspicious but expected |
| `closed` | `other` or none | Closed | Undetermined |

On close, the Argos closure reason description (or the closure reason itself when there is none) becomes the classification comment.

## Known Limitations

- **Microsoft Sentinel → Argos sync is not available.** The Argos API accepts its token only as a cookie (`Cookie: access_token=…`); it rejects the token in `Authorization`, `X-Api-Key` and query-string form. Azure Logic Apps removes the `Cookie` header from outgoing HTTP requests, so no playbook can authenticate to Argos, and status changes made in Microsoft Sentinel are not sent back. The data connector is unaffected, because the Codeless Connector Platform sends the key itself. This also affects the enrichment and response playbooks, whose Argos calls return HTTP 401. Restoring outbound sync requires the Argos API to accept the token in a normal request header.
- **Only an alert's latest change is visible.** The Argos API filters on an alert's current `update_date`, so the connector sees the state an alert is in when it polls, not every intermediate change. If another integration or script rewrites the same alerts more often than the connector polls (every 5 minutes), each poll can find nothing new and changes are missed until the rewriting stops.
- **The Argos API quota is shared per token.** Argos allows 5,000 requests per 24 hours (and 60 per minute) per API token. The connector uses about 288 requests a day, and each Exporter run makes one read and at most one write per Argos alert. Other integrations using the same token draw from the same quota; when it runs out, polling and status sync stop until requests age out of the 24-hour window. Use a dedicated token for this solution.
- **Incidents are only created for alerts first seen within 47 hours of creation.** This is the longest lookback Microsoft Sentinel allows for a rule that runs every 5 minutes.
- **Only status is mirrored.** Changing the closure reason of an alert that is already closed on both sides is not re-synced.
- **Sync latency is about 10–15 minutes** from Argos to Microsoft Sentinel: one connector poll plus one InboundStatusSync run.

## Troubleshooting

### No data in argsentdc_CL

1. Verify the CCP data connector is connected in **Data connectors**.
2. Check the API token hasn't expired.
3. Ensure the tenant URL is correct and reachable from Azure.

### Argos changes don't reach Microsoft Sentinel

1. Confirm the connector was connected under 3.2.0 or later: its request must filter on `update_date`. Reconnect it otherwise.
2. Check the **Check_Point_EM_InboundStatusSync** run history. A 403 on `Find_incidents_out_of_sync` or `Get_incident` means the managed identity lacks **Microsoft Sentinel Responder**.
3. The incident must have been created by the **Argos alerts to incidents** rule; incidents without the `ref_id` Custom Detail cannot be matched.

### Playbook calls to Argos fail with HTTP 401

Expected in this version: Azure Logic Apps removes the `Cookie` header the Argos API needs. See **Known Limitations**.

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
