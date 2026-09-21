# StratoSecure — Close In Sentinel

Closes a Microsoft Sentinel incident after a StratoSecure finding is remediated or accepted. The incident is closed as `BenignPositive - SuspiciousButExpected` and an audit record is written to `StratoSecure_PlaybookRuns_CL`.

## Prerequisites

- Microsoft Sentinel workspace with Contributor access
- StratoSecure Platform API key (generated at client.stratocode.io)

## Post-Deployment Steps

1. Grant the Logic App system-assigned managed identity the **Microsoft Sentinel Responder** role on the Sentinel workspace.
2. Configure the Sentinel automation rule to trigger this playbook when a finding is marked as remediated in StratoSecure.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PlaybookName | string | Logic App resource name |
| WorkspaceName | string | Microsoft Sentinel Log Analytics workspace name |
| LogAnalyticsWorkspaceId | string | Workspace ID for audit logging |
| LogAnalyticsWorkspaceKey | securestring | Workspace primary key for audit logging |
| RequireApproval | bool | When true, actions execute only after approval condition evaluates (default: true) |
