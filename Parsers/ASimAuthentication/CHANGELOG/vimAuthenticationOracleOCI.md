# Changelog for vimAuthenticationOracleOCI.yaml

## Version 0.2.0

- (2026-09-21) Reworked as an independent filtering parser that queries `OCI_LogsV2_CL` directly and re-implements ASim normalization logic, instead of wrapping `ASimAuthenticationOracleOCI`, to keep ASim and vim parsers separate. Removed extra unnormalized columns from the final `project`: dropped `ActingAppIdType` and `TenantId`, renamed `SrcOriginalUserAgent` to the schema field `HttpUserAgent`, and moved `TargetTenantId` into `AdditionalFields` as `TenantOcid`.

## Version 0.1.0

- (2026-09-14) First commit
