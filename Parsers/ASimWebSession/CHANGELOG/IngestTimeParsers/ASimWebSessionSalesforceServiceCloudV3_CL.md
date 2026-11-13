# Changelog for ASimWebSessionSalesforceServiceCloudV3_CL.yaml

## Version 0.2.0

- (2026-11-12) Add the Salesforce Service Cloud V3 WebSession ingestion-time definition - [PR #15657](https://github.com/Azure/Azure-Sentinel/pull/15657)
- Consume the post-connector raw-table shape; compose after the existing connector projection rather than replacing it.
- Preserve query-only fields in AdditionalFields.QueryTimeFields and the documented lossy URL rewrite; runtime validation remains outstanding.
