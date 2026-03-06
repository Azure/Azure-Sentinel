# Changelog for vimAuditEventSQLSecurityAudit.yaml

## Version 0.2.0

- (2026-03-06) Bug fix: Fixed EventSchemaVersion from "0.1.0" to "0.1.2". Fixed ActorUserId to use ServerPrincipalSid/server_principal_sid_s instead of ServerPrincipalId/server_principal_id_d. Updated ActorUserIdType from "Other" to "SID".

## Version 0.1.0

- (2026-03-03) Initial version - SQLSecurityAudit logs parser for ASIM AuditEvent schema. Supports both SQLSecurityAuditEvents dedicated table and AzureDiagnostics table.
