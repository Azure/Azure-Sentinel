# Changelog for ASimAuthenticationSalesforceLoginHistoryV2_CL.yaml

## Version 0.1.4

- (2026-11-12) Preserve query-only Login History V2 fields in AdditionalFields.QueryTimeFields and project physical destination columns - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Retain the existing parse_ipv4/parse_ipv6 source IP validation and source normalization; runtime validation remains outstanding.

## Version 0.1.2

- (2026-11-06) Inline transformation-compatible source IP validation for the Salesforce Login History V2 ingestion-time parser - [PR #15573](https://github.com/Azure/Azure-Sentinel/pull/15573)
- Support compressed IPv4-embedded IPv6, reject trailing input, and keep the transformation source-rooted without helper declarations or native IP functions.

## Version 0.1.1

- (2026-10-26) Add the ingestion-time Salesforce Login History V2 Authentication parser - [PR #15390](https://github.com/Azure/Azure-Sentinel/pull/15390)
