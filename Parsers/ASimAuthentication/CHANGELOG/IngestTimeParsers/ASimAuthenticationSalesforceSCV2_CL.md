# Changelog for ASimAuthenticationSalesforceSCV2_CL.yaml

## Version 0.2.2

- (2026-11-13) Align the Authentication schema version and unknown-user-agent OS fallback with the current query-time counterpart - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Emit EventSchemaVersion 1.0.0 and DvcOs Other for unrecognized user agents; other OS parsing remains deliberately limited.
- Preserve AdditionalFields.QueryTimeFields and the post-connector input contract; the missing V2 fixture and storage-shape parity discrepancy remain unresolved.

## Version 0.2.1

- (2026-11-12) Add the Salesforce Service Cloud V2 Authentication ingestion-time definition - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Consume the post-connector raw-table shape; compose after the existing connector projection rather than replacing it.
- Describe the unchanged EventSchemaVersion 0.1.4 output and retain query-only fields in AdditionalFields.QueryTimeFields.
- Preserve documented lossy URL/OS rewrites; runtime validation remains outstanding.
