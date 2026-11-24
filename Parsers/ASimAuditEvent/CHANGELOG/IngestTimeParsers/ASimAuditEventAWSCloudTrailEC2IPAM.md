# Changelog for ASimAuditEventAWSCloudTrailEC2IPAM.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `AWSCloudTrail EC2 IPAM AuditEvent ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.1

- (2026-11-20) Inline the event-type expression in ParserFilterQuery for where-only raw-retention compilation - [PR #15706](https://github.com/Azure/Azure-Sentinel/pull/15706)
- Preserve all event lists and row-selection behavior; leave ParserQuery unchanged.

## Version 0.1.0

- (2026-11-06) Add the ingestion-time AWS CloudTrail EC2 IPAM AuditEvent parser - [PR #15622](https://github.com/Azure/Azure-Sentinel/pull/15622)
- Normalize matching AWSCloudTrail activity into ASimAuditEventLogs.
