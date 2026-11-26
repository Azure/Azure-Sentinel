# Changelog for ASimAuditEventSalesforceAuditTrailV2_CL.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `SalesforceAuditTrailV2_CL AuditEvent ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.2

- (2026-11-06) Reduce ingestion transform length without changing mappings by grouping equivalent Section comparisons - [PR #15579](https://github.com/Azure/Azure-Sentinel/pull/15579)
- Preserve all 87 case-sensitive Section mappings, their order, and the empty fallback in six same-result groups.
- Preserve original query indentation outside the grouped Section mapping.
- Reduce ParserQuery from 16,612 to 14,283 characters and compacted KQL from 14,257 to 12,036 characters.
