# Changelog for ASimAuditEventAWSCloudTrailEC2TransitGateway.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `AWSCloudTrail EC2 Transit Gateway AuditEvent ASIM parser`.

## Version 0.1.0

- (2026-11-06) Add the ingestion-time AWS CloudTrail EC2 transit gateway AuditEvent parser - [PR #15622](https://github.com/Azure/Azure-Sentinel/pull/15622)
- Normalize matching AWSCloudTrail activity into ASimAuditEventLogs.
