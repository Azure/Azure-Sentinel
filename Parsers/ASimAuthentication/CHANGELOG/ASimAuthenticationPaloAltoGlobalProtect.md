# Changelog for ASimAuthenticationPaloAltoGlobalProtect.yaml

## Version 0.1.1

- (2026-06-02) Fixed incorrect DvcIpAddr mapping: replaced `Computer` (which contains a hostname) with `DeviceAddress` (the standard CEF device IP field).

## Version 0.1.0

- (2026-04-06) Initial ASIM Authentication parser for Palo Alto PAN-OS GlobalProtect logs from CommonSecurityLog. Supports gateway-login, gateway-logout, gateway-auth, portal-auth, portal-prelogin, and gateway-connected event types.
