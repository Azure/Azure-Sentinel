# StratoSecure — Notify Teams

Sends a Microsoft Teams notification with a summary of the triggered security incident and links to the StratoSecure finding detail.

## Prerequisites

- Microsoft Sentinel workspace
- Microsoft Teams incoming webhook URL
- StratoSecure Platform API key (generated at client.stratocode.io)

## Post-Deployment Steps

1. Grant the Logic App system-assigned managed identity the **Microsoft Sentinel Responder** role on the Sentinel workspace.
2. Configure the Teams webhook URL as a Sentinel automation rule trigger.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PlaybookName | string | Logic App resource name |
| TeamsWebhookUrl | securestring | Microsoft Teams incoming webhook URL |
| LogAnalyticsWorkspaceId | string | Workspace ID for audit logging |
| LogAnalyticsWorkspaceKey | securestring | Workspace primary key for audit logging |
| RequireApproval | bool | When true, actions execute only after approval condition evaluates (default: true) |
