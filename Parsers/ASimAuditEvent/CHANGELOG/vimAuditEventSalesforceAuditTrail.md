# Changelog for vimAuditEventSalesforceAuditTrail

## Version 0.1.0 - 2026-10-02

- (2026-10-02) Initial creation of the Salesforce Audit Trail AuditEvent filtering parser.
- Add standard AuditEvent filters for time, actor username, operation, event type, event result, object, new value, and source IP prefix.
- Apply supported filters before target/domain and identity normalization.
- Preserve source `TimeGenerated`, use `CreatedDate` for event start/end time, and support optional `AdditionalFields` packing.
