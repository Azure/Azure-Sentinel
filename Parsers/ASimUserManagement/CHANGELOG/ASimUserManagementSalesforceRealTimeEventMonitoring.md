# Changelog for ASimUserManagementSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward `disabled` and `pack` and reference the connector's guaranteed `SalesforceDomain` column directly.
- Reference the PermissionSetEventStore API and preserve documented login-history, session-level, and related-event identifiers when packing.
- Retain permission-set assignment context without fabricating group membership, target usernames, or complete before/after permission snapshots.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring UserManagement parser.
- Normalizes PermissionSetEventStore user assignments as UserModified, not group membership. Single impacted-user identifiers map to TargetUserId; bulk events remain one row and do not select an arbitrary target.
