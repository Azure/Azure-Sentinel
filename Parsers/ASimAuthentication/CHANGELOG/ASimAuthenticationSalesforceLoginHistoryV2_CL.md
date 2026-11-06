# Changelog for ASimAuthenticationSalesforceLoginHistoryV2_CL.yaml

## Version 0.1.2

- (2026-11-06) Inline source IP validation in the ingestion-time parser without top-level helpers or unavailable native IP functions.
- Preserve standard IPv4, full/compressed IPv6, IPv4-embedded IPv6, and IPv4 /0-/32 and IPv6 /0-/128 CIDR suffixes.
- Correct compressed IPv4-embedded IPv6 with groups on both sides of `::`; reject trailing whitespace and newlines.
- Nonstandard IPv4 representations (including leading-zero octets) remain excluded; no live DCR enablement is claimed.

## Version 0.1.1

- (2026-10-21) Initial ingestion-time conversion for the Salesforce Login History V2 connector route - [PR #15390](https://github.com/Azure/Azure-Sentinel/pull/15390)
