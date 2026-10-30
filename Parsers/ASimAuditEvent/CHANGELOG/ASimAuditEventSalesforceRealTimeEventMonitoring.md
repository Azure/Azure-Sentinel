# Changelog for ASimAuditEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward `disabled` and `pack` and reference the connector's guaranteed `SalesforceDomain` column directly.
- Reference the PermissionSetEventStore API and preserve documented login-history, session-level, and related-event identifiers when packing.
- Normalize enabled permissions as `NewValue`, disabled permissions as `OldValue`, affected permission sets/groups/profiles as configuration objects, and the documented event source as the acting application.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring AuditEvent parser.
- Normalizes PermissionSetEventStore permission-definition changes, excluding user-assignment operations handled by the UserManagement parser. Business-data API, report, and list-view activity is not represented as a configuration audit event.
