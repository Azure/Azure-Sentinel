# Changelog for vimUserManagementSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward all filtering and control parameters and filter before device normalization and packing.
- Reference the PermissionSetEventStore API, use the guaranteed `SalesforceDomain` column directly, and preserve documented login-history, session-level, and related-event identifiers when packing.
- Retain permission-set assignment context without fabricating group membership, target usernames, or complete before/after permission snapshots.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring UserManagement parser.
- Normalizes PermissionSetEventStore user assignments as UserModified, not group membership. Single impacted-user identifiers map to TargetUserId; bulk events remain one row and do not select an arbitrary target.
