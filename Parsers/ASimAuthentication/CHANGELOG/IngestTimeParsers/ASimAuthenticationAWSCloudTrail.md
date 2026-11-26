# Changelog for ASimAuthenticationAWSCloudTrail.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `AWSCloudTrail Sign-in Authentication ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.2.3

- (2026-11-06) Convert AwsEventId to a string for EventOriginalUid to match the native Authentication table type - [PR #15564](https://github.com/Azure/Azure-Sentinel/pull/15564)

## Version 0.2.2

- (2026-11-04) Add the ingestion-time AWS CloudTrail Authentication parser targeting ASimAuthenticationEventLogs - [PR #15546](https://github.com/Azure/Azure-Sentinel/pull/15546)
