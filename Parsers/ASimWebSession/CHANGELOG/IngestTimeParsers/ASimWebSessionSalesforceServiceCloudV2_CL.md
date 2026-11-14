# Changelog for ASimWebSessionSalesforceServiceCloudV2_CL.yaml

## Version 0.2.1

- (2026-11-13) Preserve original AdditionalFields keys without the added QueryTimeFields bag, matching established ingestion-time parsers - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Keep physical destination columns and the post-connector input contract unchanged; query-only aliases are not persisted.

## Version 0.2.0

- (2026-11-12) Add the Salesforce Service Cloud V2 WebSession ingestion-time definition - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Consume the post-connector raw-table shape; compose after the existing connector projection rather than replacing it.
- Preserve query-only fields in AdditionalFields.QueryTimeFields and the documented lossy URL rewrite; runtime validation remains outstanding.
