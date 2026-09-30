# Changelog for vimAuthenticationSalesforceLoginHistory

## Version 0.1.0 - 2026-09-30

- (2026-09-30) Initial creation of the Salesforce Login History Authentication filtering parser.
- Add standard Authentication filters for time, user, target application, source IP prefix, source hostname, event type, result details, and result.
- Resolve Salesforce target host, domain, domain type, and FQDN fields with `_ASIM_ResolveFQDN`, and identify the cloud reporting device with the event product.
- Preserve the source table's `TimeGenerated`, use `LoginTime` for the normalized event start/end time, and retain `LoginTime` under its original name in `AdditionalFields`.
- Support optional packing of unmapped Salesforce login metadata into `AdditionalFields`.
