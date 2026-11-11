# Changelog for ASimFileEventAWSCloudTrail.yaml

## Version 0.1.1

- (2026-11-11) Add the AWS CloudTrail ingestion-time FileEvent parser and preserve EventSubType parity with the query-time parser - [PR #15448](https://github.com/Azure/Azure-Sentinel/pull/15448)
- Calculate upload, download, check-in, and delete-marker subtypes in one assignment without referencing a previously assigned EventSubType.
