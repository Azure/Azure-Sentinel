# StratoSecure — Create Azure DevOps Work Item

Creates an Azure DevOps Task work item for tracking finding remediation when a Microsoft Sentinel incident is triggered from a StratoSecure finding. The work item is tagged `sentinel; stratosecure; appsec` with Priority 1.

## Prerequisites

- Microsoft Sentinel workspace
- Azure DevOps organization and project
- Azure DevOps Personal Access Token with Work Items (Read & Write) scope
- StratoSecure Platform API key (generated at client.stratocode.io)

## Post-Deployment Steps

1. Grant the Logic App system-assigned managed identity the **Microsoft Sentinel Responder** role on the Sentinel workspace.
2. Store the `AdoPat` in Azure Key Vault and reference it in the parameter.
3. Verify the `AdoOrganization` and `AdoProject` values match your ADO environment.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PlaybookName | string | Logic App resource name |
| AdoOrganization | string | Azure DevOps organization name |
| AdoProject | string | Azure DevOps project name |
| AdoPat | securestring | Personal Access Token with Work Items (Read & Write) scope |
| LogAnalyticsWorkspaceId | string | Workspace ID for audit logging |
| LogAnalyticsWorkspaceKey | securestring | Workspace primary key for audit logging |
| RequireApproval | bool | When true, actions execute only after approval condition evaluates (default: true) |
