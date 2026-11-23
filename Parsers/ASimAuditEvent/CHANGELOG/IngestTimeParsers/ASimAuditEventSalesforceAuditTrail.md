# Changelog for ASimAuditEventSalesforceAuditTrail.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `SentinelSalesforceAuditTrail AuditEvent ASIM parser`.

## Version 0.1.2

- (2026-11-06) Reduce ingestion-time transform length with equivalent grouped Section mappings - [PR #15578](https://github.com/Azure/Azure-Sentinel/pull/15578)
- Preserve all Section string literals, mapping precedence, fallback behavior, and normalized output fields.
