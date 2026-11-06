# Changelog for ASimAuditEventSalesforceAuditTrail.yaml

## Version 0.1.2

- (2026-11-06) Reduce ingestion-time transform length with equivalent grouped Section mappings - [PR #15578](https://github.com/Azure/Azure-Sentinel/pull/15578)
- Preserve all Section string literals, mapping precedence, fallback behavior, and normalized output fields.
- Keep the internal `_srcHost1` alias in scope through host-derived field calculations, then omit it from the explicit output projection.
