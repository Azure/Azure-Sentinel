# Changelog for ASimAuditEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring AuditEvent parser.
- Normalizes PermissionSetEventStore permission-definition changes, excluding user-assignment operations handled by the UserManagement parser. Business-data API, report, and list-view activity is not represented as a configuration audit event.
