# Check Point Exposure Management - Importer (Argos Status Changes → Sentinel)

## Summary

This playbook polls Argos for recently modified alerts and writes updated records to the `argsentdc_CL` custom Log Analytics table. It complements the CCP data connector which only ingests **new** alerts (using `created_date`). The Importer catches **status changes**, closures, and other alert updates using the `modification_date` filter.

**Flow:**
1. Runs on a configurable recurrence interval (default: 10 minutes).
2. Calls **Check_Point_EM_Base** to retrieve API credentials.
3. Calculates the polling time window (last N minutes) as Unix timestamps.
4. Polls alerts API with `modification_date` filter.
5. For each modified alert, writes the updated record to the custom table via the Data Collection API.
6. Tracks success/error counts per run.

## Prerequisites

1. **Check_Point_EM_Base** playbook must be deployed in the same resource group.
2. A valid Check Point Exposure Management API token configured in the Check_Point_EM_Base Key Vault.
3. The CCP data connector must be deployed (provides the Data Collection Endpoint and Data Collection Rule).

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_Importer%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_Importer`) |
| **Check_Point_EM_Base_PlaybookName** | No | Name of the base playbook (default: `Check_Point_EM_Base`) |
| **PollingIntervalMinutes** | No | Poll interval in minutes (default: `10`) |
| **DataCollectionEndpoint** | Yes | DCE URL from the CCP connector deployment |
| **DataCollectionRuleImmutableId** | Yes | DCR immutable ID from the CCP connector deployment |

## Post-Deployment

1. The ARM template automatically assigns the **Monitoring Metrics Publisher** role to the Logic App's Managed Identity.
2. Verify the Recurrence trigger is running at the configured interval in the Logic App run history.

## Deduplication

If the same alert appears in both the CCP connector (new) and Importer (modified) within the same window, the table will have two rows with the same `ref_id`. This is expected — analytics rules should use `arg_max(TimeGenerated, *)` by `ref_id` to get the latest state.

## Error Handling

- HTTP requests use exponential backoff retry policy (3 retries) for 429/5xx errors.
- Per-record errors are counted but don't block remaining records.
- Success and error counts are tracked per run for monitoring via Logic App run history.

## API Endpoints Used

| Action | Endpoint |
|--------|----------|
| Poll modified alerts | `POST {ArgosBaseUrl}` with `modification_date` filter |
| Write to custom table | `POST {DCE}/dataCollectionRules/{dcr_id}/streams/Custom-argsentdc_CL` |
