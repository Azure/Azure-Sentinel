# Changelog for ASimWebSessionSalesforceServiceCloud.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `SalesforceServiceCloudV3_CL WebSession ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.2.1

- (2026-11-11) Fall back to ResponseSize when the source DstBytes value is empty - [PR #15651](https://github.com/Azure/Azure-Sentinel/pull/15651)

## Version 0.2.0

- (2026-09-15) Add the ingestion-time Salesforce Service Cloud WebSession parser targeting ASimWebSessionLogs - [PR #15136](https://github.com/Azure/Azure-Sentinel/pull/15136)
- Normalize web session and API request events from SalesforceServiceCloudV3_CL.
