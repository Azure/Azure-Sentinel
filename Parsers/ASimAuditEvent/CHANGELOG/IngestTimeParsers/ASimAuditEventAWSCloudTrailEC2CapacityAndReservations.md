# Changelog for ASimAuditEventAWSCloudTrailEC2CapacityAndReservations.yaml

## Version 0.1.1

- (2026-11-20) Inline the event-type expression in ParserFilterQuery for where-only raw-retention compilation - [PR #15706](https://github.com/Azure/Azure-Sentinel/pull/15706)
- Preserve all event lists and row-selection behavior; leave ParserQuery unchanged.

## Version 0.1.0

- (2026-11-06) Add the ingestion-time AWS CloudTrail EC2 capacity and reservations AuditEvent parser - [PR #15622](https://github.com/Azure/Azure-Sentinel/pull/15622)
- Normalize matching AWSCloudTrail activity into ASimAuditEventLogs.
