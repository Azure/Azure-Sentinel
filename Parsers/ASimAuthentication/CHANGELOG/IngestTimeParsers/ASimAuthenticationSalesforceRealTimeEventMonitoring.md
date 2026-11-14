# Changelog for ASimAuthenticationSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.2

- (2026-11-13) Preserve original AdditionalFields keys without the added QueryTimeFields bag, matching established ingestion-time parsers - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Keep physical destination columns and native/integer-octet IP normalization unchanged; query-only aliases are not persisted.

## Version 0.1.1

- (2026-11-13) Replace unsupported ingestion-time format_ipv4 with integer octet formatting for hexadecimal IPv4-mapped addresses - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Preserve native IPv4/IPv6 validation, empty output for invalid mapped addresses, and AdditionalFields.QueryTimeFields.

## Version 0.1.0

- (2026-11-12) Add the Salesforce Real-Time Event Monitoring Authentication ingestion-time definition - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Use the source EventIdentifier rather than pre-ingestion _ItemId and retain it in AdditionalFields.QueryTimeFields.
- Preserve documented lossy URL/OS rewrites and the physical storage shape; runtime validation remains outstanding.
