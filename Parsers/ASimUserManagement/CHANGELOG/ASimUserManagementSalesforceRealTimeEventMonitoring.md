# Changelog for ASimUserManagementSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward `disabled` and `pack` and reference the connector's guaranteed `SalesforceDomain` column directly.
- Reference the PermissionSetEventStore API and preserve documented login-history, session-level, and related-event identifiers when packing.
- Normalize assigned and unassigned permission-set or permission-set-group values as `NewPropertyValue` and `PreviousPropertyValue`, and the documented event source as the acting application, without fabricating group membership or target usernames.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring UserManagement parser.
- Normalizes PermissionSetEventStore user assignments as UserModified, not group membership. Single impacted-user identifiers map to TargetUserId; bulk events remain one row and do not select an arbitrary target.
