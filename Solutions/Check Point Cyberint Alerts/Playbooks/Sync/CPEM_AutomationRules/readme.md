# Check Point Exposure Management - Automation Rules for Bi-Directional Sync

## Summary

Deploys a Microsoft Sentinel automation rule that runs the **Check_Point_EM_Exporter** playbook whenever an incident's status changes.

**Rule:** When an incident's status changes to New, Active or Closed → run Check_Point_EM_Exporter.

## Prerequisites

1. **Check_Point_EM_Exporter** playbook must be deployed in the same resource group.
2. Microsoft Sentinel must be enabled on the target Log Analytics workspace.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FSync%2FCPEM_AutomationRules%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name identifying this deployment; seeds the rule's resource name (default: `Check_Point_EM_AutomationRules`) |
| **Sentinel_Workspace_Resource_Id** | Yes | Full resource ID of the Log Analytics workspace with Sentinel enabled |
| **Exporter_PlaybookName** | No | Name of the Exporter Logic App (default: `Check_Point_EM_Exporter`) |
| **Automation_Rule_Order** | No | Execution priority (default: `100`, lower = higher priority) |

### Finding your workspace resource ID

```bash
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --query id -o tsv
```

## Loop Prevention

Status changes flow both ways: the **Check_Point_EM_InboundStatusSync** playbook applies Argos changes to incidents, and this rule sends incident changes to Argos. The two directions do not echo each other because:

1. The Exporter reads each Argos alert before writing and skips it when Argos already has the target status (and closure reason, when closing).
2. InboundStatusSync only updates an incident whose status differs from Argos and whose last status change is older than the Argos change.

A status change applied by InboundStatusSync still fires this rule, but the Exporter then finds Argos already in that state and sends nothing.
