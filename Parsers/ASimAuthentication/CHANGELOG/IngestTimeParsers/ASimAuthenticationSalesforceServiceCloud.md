# Changelog for ASimAuthenticationSalesforceServiceCloud.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `SalesforceServiceCloudV3_CL Authentication ASIM parser`.

## Version 0.2.3

- (2026-11-10) Align EventSchemaVersion and unknown device operating-system values with the query-time parser - [PR #15651](https://github.com/Azure/Azure-Sentinel/pull/15651)

## Version 0.2.2

- (2026-11-06) Reduce the Salesforce Service Cloud ingestion-time transform size - [PR #15580](https://github.com/Azure/Azure-Sentinel/pull/15580)
- Share exact login-status membership, group equivalent mappings, and remove unprojected original logon mappings.
