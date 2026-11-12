# Changelog for ASimAuthenticationSalesforceSCV2_CL.yaml

## Version 0.2.1

- (2026-11-12) Add the Salesforce Service Cloud V2 Authentication ingestion-time definition.
- Consume the post-connector raw-table shape; compose after the existing connector projection rather than replacing it.
- Describe the unchanged EventSchemaVersion 0.1.4 output and retain query-only fields in AdditionalFields.QueryTimeFields.
- Preserve documented lossy URL/OS rewrites; runtime validation remains outstanding.
