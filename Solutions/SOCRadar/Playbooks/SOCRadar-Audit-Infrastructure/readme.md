# SOCRadar Audit Infrastructure

Creates the Log Analytics custom table and Data Collection Rule for SOCRadar audit logging.

## Resources Created

- **Custom Table** (SOCRadarAuditLog_CL) with audit fields
- **Data Collection Rule** (SOCRadar-Audit-DCR)

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| WorkspaceName | Log Analytics Workspace Name | Required |
| TableRetentionDays | Retention for audit logs (7-730 days) | 30 |

## Deploy

Deploy this before enabling audit logging in the Import playbook.
