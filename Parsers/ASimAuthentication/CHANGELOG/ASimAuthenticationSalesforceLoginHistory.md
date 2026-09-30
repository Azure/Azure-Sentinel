# Changelog for ASimAuthenticationSalesforceLoginHistory

## Version 0.1.0 - 2026-09-30

- (2026-09-30) Initial creation of the Salesforce Login History Authentication parser.
- Normalize login result, method, protocol, source IP, source geography, target application, user ID, and client platform fields.
- Resolve Salesforce target host, domain, domain type, and FQDN fields with `_ASIM_ResolveFQDN`, and identify the cloud reporting device with the event product.
- Support optional packing of unmapped Salesforce login metadata into `AdditionalFields`.
