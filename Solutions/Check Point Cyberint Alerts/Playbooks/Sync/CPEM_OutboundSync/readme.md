# Check Point Exposure Management - Exporter (Sentinel → Argos)

## Summary

When a Microsoft Sentinel incident status changes, this playbook pushes the new status to the corresponding Argos alert(s). It maps the incident status, classification and classification reason to the Argos status and closure reason.

**Flow:**
1. Triggered by the **Check_Point_EM_AutomationRules** rule when an incident's status changes.
2. Skips incidents with no alerts attached.
3. Maps the Microsoft Sentinel status to the Argos status, and on close, the classification to a closure reason.
4. Collects the distinct `ref_id` Custom Details of the attached alerts, so each Argos alert is handled once even when several incident alerts share it.
5. For each `ref_id`, fetches the Argos alert and skips it when Argos already matches: same status, and when closing, either the same closure reason or a closure reason that maps back to the incident's classification (see below). Otherwise sends `PUT /alert/api/v1/alerts/status`.
6. Adds a sync result comment and tags the incident `argos-exporter-synced`.

## Prerequisites

1. A valid Check Point Exposure Management API token.
2. Incidents created by the **Check Point Exposure Management - Argos alerts to incidents** analytic rule, which provides the `ref_id` Custom Detail.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_OutboundSync%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_Exporter`) |
| **API_Base_URL** | Yes | Tenant URL, the same value as the data connector's Argos URL (e.g. `https://your_tenant.cyberint.io`). Any path is ignored; `/alert` is added automatically. |
| **API_Access_Token** | Yes | Check Point Exposure Management API token |

## Post-Deployment

1. Grant the Logic App Managed Identity the **Microsoft Sentinel Responder** role on the resource group.
2. Deploy **Check_Point_EM_AutomationRules** so this playbook runs on every incident status change.

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

Several Argos closure reasons map to Benign Positive in the inbound direction (`no_longer_a_threat`, `irrelevant`, `asset_should_not_be_monitored`, `asset_belongs_to_my_organization`, `asm_no_longer_detected`, `asm_manually_closed`). When an incident closed as Benign Positive belongs to an Argos alert already closed with any of these, the Exporter leaves the Argos reason unchanged rather than replacing it with `no_longer_a_threat`.

## Loop Prevention

The **Check_Point_EM_InboundStatusSync** playbook applies Argos changes to incidents, which fires this playbook again. Because the Exporter reads the Argos alert first and skips alerts already in the target state, those changes are not sent back.

## API Endpoints Used

| Action | Endpoint |
|--------|----------|
| Get alert | `GET /alert/api/v1/alerts/{alert_ref_id}` |
| Update alert status | `PUT /alert/api/v1/alerts/status` |
