# Changelog for ASimWebSessionSalesforceServiceCloudV2_CL.yaml

## Version 0.2.0

- (2026-11-12) Add the Salesforce Service Cloud V2 WebSession ingestion-time definition.
- Consume the post-connector raw-table shape; compose after the existing connector projection rather than replacing it.
- Preserve query-only fields in AdditionalFields.QueryTimeFields and the documented lossy URL rewrite; runtime validation remains outstanding.
