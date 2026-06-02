# Changelog for ASimAuthenticationPaloAltoPanOS.yaml

## Version 0.1.1

- (2026-06-02) Fixed incorrect DvcIpAddr mapping: replaced `Computer` (which contains a hostname) with `DeviceAddress` (the standard CEF device IP field). Removed redundant DvcHostname override that was clobbering the correct value from `_ASIM_ResolveDvcFQDN`.

## Version 0.1.0

- (2026-04-01) Initial version of ASIM Authentication parser for Palo Alto PAN-OS.
- Normalizes PAN-OS authentication events from CommonSecurityLog to ASIM Authentication schema v0.1.3.
- Maps auth-success, auth-fail, and auth-error Activity values to EventResult.
- Supports filtering parameters: starttime, endtime, username_has_any, srcipaddr_has_any_prefix, srchostname_has_any, eventtype_in, eventresultdetails_in, eventresult.
