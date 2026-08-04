# Check Point Exposure Management - Automation Rules for Bi-Directional Sync

## Summary

Deploys a Microsoft Sentinel automation rule that triggers the **Check_Point_EM_Exporter** playbook when an incident is updated. The playbook itself handles filtering (only processes status changes) and loop prevention (skips if `argos-importer-synced` tag is present).

**Rule:** When any incident is updated → run Check_Point_EM_Exporter.

## Prerequisites

1. **Check_Point_EM_Exporter** playbook must be deployed in the same resource group.
2. Microsoft Sentinel must be enabled on the target Log Analytics workspace.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_AutomationRules%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **SentinelWorkspaceResourceId** | Yes | Full resource ID of the Log Analytics workspace with Sentinel enabled |
| **ExporterPlaybookName** | No | Name of the Exporter Logic App (default: `Check_Point_EM_Exporter`) |
| **AutomationRuleOrder** | No | Execution priority (default: `100`, lower = higher priority) |

### Finding your workspace resource ID

```bash
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --query id -o tsv
```

## Loop Prevention

The automation rule triggers on **all** incident updates. Loop prevention is handled by the Exporter playbook:

1. Playbook checks if `argos-importer-synced` tag is present → skips sync if so.
2. Playbook checks if the `Status` field changed → skips if not.
3. Only when both checks pass does it push the status to Argos.

This design keeps the automation rule simple and centralizes the filtering logic in the playbook.
