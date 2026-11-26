# Changelog for ASimAuthenticationSalesforceLoginHistory.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `SentinelSalesforceLoginHistory Authentication ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.2

- (2026-11-06) Inline transformation-compatible source IP validation for the Salesforce Login History ingestion-time parser - [PR #15573](https://github.com/Azure/Azure-Sentinel/pull/15573)
- Support compressed IPv4-embedded IPv6, reject trailing input, and keep the transformation source-rooted without helper declarations or native IP functions.

## Version 0.1.1

- (2026-10-26) Add the ingestion-time Salesforce Login History Authentication parser - [PR #15390](https://github.com/Azure/Azure-Sentinel/pull/15390)
