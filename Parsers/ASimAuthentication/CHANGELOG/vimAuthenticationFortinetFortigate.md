# Changelog for vimAuthenticationFortinetFortigate.yaml

## Version 0.1.1

- (2026-06-23) Extended the parser to normalize FortiGate admin authentication events sent in the `event:system` CEF format. Login and logout events are now routed by `DeviceAction` (`login`/`logout`), and the parser matches the `Activity` values `event:system failed` and `event:system success` in addition to the existing `system event login`/`system event logout` (IcM 51000001072360).

## Version 0.1.0

- (2026-03-10) Initial parser for Fortinet - Fortigate logs in CommonSecurityLog - [PR #13786](https://github.com/Azure/Azure-Sentinel/pull/13786)

