# Changelog for ASimAuthenticationSalesforceLoginHistory

## Version 0.1.0 - 2026-10-01

- (2026-10-01) Initial creation of the Salesforce Login History Authentication parser.
- Normalize login result, method, protocol, source IP, source geography, target application, user ID, and client platform fields.
- Prefer the optional native `SalesforceDomain` column for target resolution, with parsed `LoginUrl` as a backward-compatible fallback.
- Resolve Salesforce target host, domain, domain type, and FQDN fields with `_ASIM_ResolveFQDN`, and identify the cloud reporting device with the event product.
- Use `project-rename` for all safe one-to-one source mappings, including application IDs/types, event type/subtype, product version, browser, platform, and country.
- Preserve the source table's `TimeGenerated`, use `LoginTime` for the normalized event start/end time, and retain `LoginTime` under its original name in `AdditionalFields`.
- Populate `SrcIpAddr`, `IpAddr`, and `Src` only when `SourceIp` parses as IPv4 or IPv6, while retaining the raw value in `AdditionalFields`.
- Support optional packing of unmapped Salesforce login metadata into `AdditionalFields`.
