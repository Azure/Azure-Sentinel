# Changelog for ASimAuditEventAWSCloudTrailEC2AccountAndInfrastructure.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `AWSCloudTrail EC2 Account and Infrastructure AuditEvent ASIM parser`.

## Version 0.1.0

- (2026-11-06) Add the ingestion-time AWS CloudTrail EC2 account and infrastructure AuditEvent parser - [PR #15586](https://github.com/Azure/Azure-Sentinel/pull/15586)
- Normalize matching AWSCloudTrail activity into ASimAuditEventLogs.
