# Changelog for ASimAlertEventAWSGuardDuty.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `AWSGuardDuty AlertEvent ASIM parser`.

## Version 0.1.1

- (2026-11-09) Escape both count property accesses in ServiceDetails for ingestion-time KQL compatibility - [PR #15597](https://github.com/Azure/Azure-Sentinel/pull/15597)
