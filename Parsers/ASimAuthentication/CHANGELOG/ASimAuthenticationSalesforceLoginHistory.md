# Changelog for ASimAuthenticationSalesforceLoginHistory

## Version 0.1.0 - 2026-09-30

- (2026-09-30) Initial creation of the Salesforce Login History Authentication parser.
- Normalize login result, method, protocol, source IP, source geography, target application, user ID, and client platform fields.
- Resolve Salesforce target host, domain, domain type, and FQDN fields with `_ASIM_ResolveFQDN`, and identify the cloud reporting device with the event product.
- Preserve the source table's `TimeGenerated`, use `LoginTime` for the normalized event start/end time, and retain `LoginTime` under its original name in `AdditionalFields`.
- Populate `SrcIpAddr`, `IpAddr`, and `Src` only when `SourceIp` parses as IPv4 or IPv6, while retaining the raw value in `AdditionalFields`.
- Support optional packing of unmapped Salesforce login metadata into `AdditionalFields`.
