# StratoSecure — Escalate Owner

Sends an escalation email via Azure Communication Services when a StratoSecure finding remains unresolved past SLA. Writes an audit record to `StratoSecure_PlaybookRuns_CL` regardless of email outcome.

## Prerequisites

- Microsoft Sentinel workspace
- Azure Communication Services resource with a verified sender domain
- StratoSecure Platform API key (generated at client.stratocode.io)

## Post-Deployment Steps

1. Grant the Logic App system-assigned managed identity the **Microsoft Sentinel Responder** role on the Sentinel workspace.
2. Grant the managed identity the **Azure Communication Services Contributor** role (or use `AcsAccessKey` parameter instead).
3. Set the `EscalationEmail` parameter to your SOC lead address.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PlaybookName | string | Logic App resource name |
| AcsEndpointHostname | string | ACS resource hostname (without https://) |
| AcsManagedIdentityEnabled | string | true to use managed identity; false to use access key |
| AcsAccessKey | securestring | ACS access key (required only when managed identity is disabled) |
| SenderEmail | string | Verified sender address in ACS |
| EscalationEmail | string | Recipient email for escalation notifications |
| LogAnalyticsWorkspaceId | string | Workspace ID for audit logging |
| LogAnalyticsWorkspaceKey | securestring | Workspace primary key for audit logging |
| RequireApproval | bool | When true, actions execute only after approval condition evaluates (default: true) |
