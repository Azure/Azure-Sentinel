# Changelog for vimUserManagementSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring UserManagement parser.
- Normalizes PermissionSetEventStore user assignments as UserModified, not group membership. Single impacted-user identifiers map to TargetUserId; bulk events remain one row and do not select an arbitrary target.
