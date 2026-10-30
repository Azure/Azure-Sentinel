# Changelog for vimAuditEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward all filtering and control parameters and apply each filter as soon as its required fields are available, before device normalization and packing.
- Reference the PermissionSetEventStore API, use the guaranteed `SalesforceDomain` column directly, and preserve documented login-history, session-level, and related-event identifiers when packing.
- Normalize enabled permissions as `NewValue`, disabled permissions as `OldValue`, affected permission sets/groups/profiles as configuration objects, and the documented event source as the acting application. The `newvalue_has_any` filter now evaluates the normalized permission values.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring AuditEvent parser.
- Normalizes PermissionSetEventStore permission-definition changes, excluding user-assignment operations handled by the UserManagement parser. Business-data API, report, and list-view activity is not represented as a configuration audit event.
