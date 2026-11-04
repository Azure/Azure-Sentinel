# Changelog for ASimUserManagementSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0

- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring UserManagement parser. - [PR #15514](https://github.com/Azure/Azure-Sentinel/pull/15514)
- Forward `disabled` and `pack`.
- Support RDA tables without `SalesforceDomain` or `Type`: leave domain-derived fields empty when the domain column is absent and use the source table name when `Type` is absent. - [PR #15514](https://github.com/Azure/Azure-Sentinel/pull/15514)
- Reference the PermissionSetEventStore API and preserve documented login-history, session-level, and related-event identifiers when packing.
- Normalize assigned and unassigned permission-set or permission-set-group values as `NewPropertyValue` and `PreviousPropertyValue`, and the documented event source as the acting application, without fabricating group membership or target usernames.
- Normalizes PermissionSetEventStore user assignments as UserModified, not group membership. Single impacted-user identifiers map to TargetUserId; bulk events remain one row and do not select an arbitrary target.
