# StratoSecure — Create Exception

Creates a risk exception in StratoSecure for accepted risks. When a Microsoft Sentinel incident is triaged as accepted risk, this playbook calls the StratoSecure API to create a 30-day exception for the finding and writes an audit record to `StratoSecure_PlaybookRuns_CL`.

## Prerequisites

- Microsoft Sentinel workspace
- StratoSecure Platform API key with exception-create permission (generated at client.stratocode.io)

## Post-Deployment Steps

1. Grant the Logic App system-assigned managed identity the **Microsoft Sentinel Responder** role on the Sentinel workspace.
2. Store the `StratoApiKey` in Azure Key Vault and reference it in the parameter.
3. Configure the Sentinel automation rule to trigger this playbook when an incident is set to "Accepted Risk" classification.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PlaybookName | string | Logic App resource name |
| StratoApiBaseUrl | string | StratoSecure platform API base URL (default: https://api.stratocode.io) |
| StratoApiKey | securestring | StratoSecure API key |
| LogAnalyticsWorkspaceId | string | Workspace ID for audit logging |
| LogAnalyticsWorkspaceKey | securestring | Workspace primary key for audit logging |
| RequireApproval | bool | When true, actions execute only after approval condition evaluates (default: true) |
