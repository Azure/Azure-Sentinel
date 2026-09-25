# Changelog for ASimAuthenticationOracleOCI.yaml

## Version 0.2.0

- (2026-09-21) Removed extra unnormalized columns from the final `project`: dropped `ActingAppIdType` and `TenantId`, renamed `SrcOriginalUserAgent` to the schema field `HttpUserAgent`, and moved `TargetTenantId` into `AdditionalFields` as `TenantOcid`.

## Version 0.1.0

- (2026-09-14) First commit
