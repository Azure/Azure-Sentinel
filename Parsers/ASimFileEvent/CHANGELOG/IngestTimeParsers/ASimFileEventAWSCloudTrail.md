# Changelog for ASimFileEventAWSCloudTrail.yaml

## Version 0.1.2

- (2026-11-11) Make the delete-marker subtype condition null-safe for empty ResponseElements and missing markers - [PR #15448](https://github.com/Azure/Azure-Sentinel/pull/15448)
- Convert the marker to a string before comparison so absent values compare as false.

## Version 0.1.1

- (2026-11-11) Add the AWS CloudTrail ingestion-time FileEvent parser and preserve EventSubType parity with the query-time parser - [PR #15448](https://github.com/Azure/Azure-Sentinel/pull/15448)
- Calculate upload, download, check-in, and delete-marker subtypes in one assignment without referencing a previously assigned EventSubType.
