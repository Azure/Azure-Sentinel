# Check Point Exposure Management - Exporter (Sentinel → Argos)

## Summary

When a Microsoft Sentinel incident status changes, this playbook pushes the update to the corresponding alert(s). It maps Sentinel incident status and close classification to alert status and closure reason. Includes tag-based loop prevention to avoid circular sync with the Importer playbook.

**Flow:**
1. Calls **Check_Point_EM_Base** to retrieve API credentials.
2. Checks for loop prevention tag (`argos-importer-synced`) — skips if present.
3. Verifies this is an incident update (not creation) and that the Status field changed.
4. Maps Sentinel status → Argos status (`Active` → `open`, `Closed` → `closed` + closure reason).
5. For each linked alert, sends HTTP PUT to update the alert status.
6. Adds a sync result comment and tags the incident `argos-exporter-synced`.

## Prerequisites

1. **Check_Point_EM_Base** playbook must be deployed in the same resource group.
2. A valid Check Point Exposure Management API token configured in the Check_Point_EM_Base Key Vault.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_Exporter%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_Exporter`) |
| **Check_Point_EM_Base_PlaybookName** | No | Name of the base playbook (default: `Check_Point_EM_Base`) |

## Post-Deployment

1. Grant the Logic App Managed Identity the **Microsoft Sentinel Responder** role on the resource group.
2. Configure an automation rule in Microsoft Sentinel to trigger this playbook on incident status changes.

## Status Mapping

| Sentinel Status | Sentinel Classification | Argos Status | Argos Closure Reason |
|----------------|------------------------|--------------|---------------------|
| Active | — | `open` | — |
| Closed | True Positive | `closed` | `true_positive` |
| Closed | False Positive | `closed` | `false_positive` |
| Closed | Benign Positive | `closed` | `benign_positive` |
| Closed | Undetermined | `closed` | `undetermined` |

## Loop Prevention

This playbook checks for the `argos-importer-synced` tag before syncing. If the tag is present (set by Importer), the playbook skips the update to prevent circular sync loops.

## API Endpoints Used

| Action | Endpoint |
|--------|----------|
| Update alert status | `PUT /api/v1/alerts/{alert_ref_id}` |
