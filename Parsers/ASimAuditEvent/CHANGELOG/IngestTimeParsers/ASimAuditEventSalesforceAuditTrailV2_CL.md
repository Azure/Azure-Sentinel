# Changelog for ASimAuditEventSalesforceAuditTrailV2_CL.yaml

## Version 0.1.4

- (2026-11-13) Preserve original AdditionalFields keys without the added QueryTimeFields bag, matching established ingestion-time parsers - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Keep physical destination columns unchanged; query-only aliases are not persisted.

## Version 0.1.3

- (2026-11-12) Preserve query-only Audit Trail V2 fields in AdditionalFields.QueryTimeFields and project physical destination columns - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Retain the existing grouped Section mappings, localized KQL escapes, source normalization, and filter; runtime validation remains outstanding.

## Version 0.1.2

- (2026-11-06) Reduce ingestion transform length without changing mappings by grouping equivalent Section comparisons - [PR #15579](https://github.com/Azure/Azure-Sentinel/pull/15579)
- Preserve all 87 case-sensitive Section mappings, their order, and the empty fallback in six same-result groups.
- Preserve original query indentation outside the grouped Section mapping.
- Reduce ParserQuery from 16,612 to 14,283 characters and compacted KQL from 14,257 to 12,036 characters.
