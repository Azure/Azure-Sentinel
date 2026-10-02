# Changelog for ASimAuditEventSalesforceAuditTrail

## Version 0.1.0 - 2026-10-02

- (2026-10-02) Initial creation of the Salesforce Audit Trail AuditEvent parser.
- Normalize Salesforce setup action, section, display message, actor identity, event identifier, and Salesforce domain fields.
- Infer ASIM audit event types from action and display verbs while defaulting configuration changes to `Set`.
- Preserve source `TimeGenerated`, use `CreatedDate` for event start/end time, and support optional `AdditionalFields` packing.
