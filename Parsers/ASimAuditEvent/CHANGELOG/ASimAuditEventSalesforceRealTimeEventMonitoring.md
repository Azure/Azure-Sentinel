# Changelog for ASimAuditEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0

- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring AuditEvent parser. - [PR #15514](https://github.com/Azure/Azure-Sentinel/pull/15514)
- Forward `disabled` and `pack`.
- Support RDA tables without `SalesforceDomain` or `Type`: leave domain-derived fields empty when the domain column is absent and use the source table name when `Type` is absent. - [PR #15514](https://github.com/Azure/Azure-Sentinel/pull/15514)
- Reference the PermissionSetEventStore API and preserve documented login-history, session-level, and related-event identifiers when packing.
- Normalize enabled permissions as `NewValue`, disabled permissions as `OldValue`, affected permission sets/groups/profiles as configuration objects, and the documented event source as the acting application.
- Normalizes PermissionSetEventStore permission-definition changes, excluding user-assignment operations handled by the UserManagement parser. Business-data API, report, and list-view activity is not represented as a configuration audit event.
