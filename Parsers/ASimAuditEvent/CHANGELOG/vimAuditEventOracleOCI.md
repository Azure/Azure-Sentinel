# Changelog for vimAuditEventOracleOCI.yaml

## Version 0.2.0

- (2026-09-21) Reworked as an independent filtering parser that queries `OCI_LogsV2_CL` directly and re-implements ASim normalization logic, instead of wrapping `ASimAuditEventOracleOCI`, to keep ASim and vim parsers separate. Removed extra unnormalized columns from the final `project`: dropped `ActingAppIdType` and `TenantId`, merged `Object`/`ObjectName` into `Object`/`ObjectId`, renamed `Url` to `TargetUrl` and `HttpUserAgentOriginal` to `HttpUserAgent`, and moved `EventTenantId` into `AdditionalFields` as `TenantOcid`.

## Version 0.1.1

- (2026-09-14) Tracks ASimAuditEventOracleOCI 0.1.1 (mandatory `Object` field fallback fix).

## Version 0.1.0

- (2026-09-14) First commit
