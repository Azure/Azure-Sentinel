# Check Point Exposure Management - Manual Status Update (Sentinel → Argos)


> **Not shipped in solution 3.2.0.** The Argos API accepts its token only as a cookie, and Azure Logic Apps removes the `Cookie` header from outgoing requests, so this playbook cannot authenticate to Argos (HTTP 401). The template is kept here for the day the Argos API accepts the token in a normal request header. See **Known Limitations** in the solution README.

## Summary

On-demand playbook that reads the current Sentinel incident status and pushes it to the corresponding alert(s). Analysts trigger this manually from the incident Actions menu when they want to explicitly sync status to Argos.

**Flow:**
1. Reads the current incident status and close classification.
2. Maps Sentinel status → Argos status and closure reason.
3. For each linked alert, sends `PUT /alert/api/v1/alerts/status` to update the alert status.
4. Adds a sync result comment and tags the incident `argos-manual-synced`.

## Prerequisites

1. A valid Check Point Exposure Management API token.
2. Incidents created by the **Check Point Exposure Management - Argos alerts to incidents** analytic rule, which provides the `ref_id` Custom Detail.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_ManualStatusUpdate%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_ManualStatusUpdate`) |
| **API_Base_URL** | Yes | Tenant URL, the same value as the data connector's Argos URL (e.g. `https://your_tenant.cyberint.io`). Any path is ignored; `/alert` is added automatically. |
| **API_Access_Token** | Yes | Check Point Exposure Management API token |

## Post-Deployment

1. Grant the Logic App Managed Identity the **Microsoft Sentinel Responder** role on the resource group.
2. Analysts can run this playbook from the Sentinel incident **Actions > Run playbook** menu.

## Status Mapping

| Microsoft Sentinel status | Classification / reason | Argos status | Argos closure reason |
|---|---|---|---|
| New | — | `open` | — |
| Active | — | `acknowledged` | — |
| Closed | True Positive | `closed` | `resolved` |
| Closed | Benign Positive | `closed` | `no_longer_a_threat` |
| Closed | False Positive / Incorrect alert logic | `closed` | `false_positive` |
| Closed | False Positive / Inaccurate data | `closed` | `irrelevant_alert_subtype` |
| Closed | Undetermined | `closed` | `other`, with the classification comment as the description (`undetermined` when empty) |

## API Endpoints Used

| Action | Endpoint |
|--------|----------|
| Update alert status | `PUT /alert/api/v1/alerts/status` |
