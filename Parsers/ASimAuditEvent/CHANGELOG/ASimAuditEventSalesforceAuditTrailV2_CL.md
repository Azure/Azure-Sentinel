# Changelog for ASimAuditEventSalesforceAuditTrailV2_CL.yaml

## Version 0.1.2

- (2026-11-06) Reduce ingestion transform length without changing mappings by grouping equivalent Section comparisons and removing query indentation - [PR #15579](https://github.com/Azure/Azure-Sentinel/pull/15579)
- Preserve all 87 case-sensitive Section mappings, their order, and the empty fallback in six same-result groups.
- Reduce ParserQuery from 16,612 to 12,037 characters and compacted KQL from 14,257 to 12,036 characters.
