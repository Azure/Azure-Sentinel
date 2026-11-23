# Changelog for ASimWebSessionSalesforceRealTimeEventMonitoring.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `SalesForceRealTimeEventMonitoring_CL WebSession ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.1

- (2026-11-13) Preserve original AdditionalFields keys without the added QueryTimeFields bag, matching established ingestion-time parsers - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Keep physical destination columns unchanged; query-only aliases are not persisted.

## Version 0.1.0

- (2026-11-12) Add the Salesforce Real-Time Event Monitoring WebSession ingestion-time definition - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Use the source EventIdentifier rather than pre-ingestion _ItemId and retain it in AdditionalFields.QueryTimeFields.
- Preserve documented lossy URL rewrites and the physical storage shape; runtime validation remains outstanding.
