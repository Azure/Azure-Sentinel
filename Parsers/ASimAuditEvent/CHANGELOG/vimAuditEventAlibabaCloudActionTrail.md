# Changelog for vimAuditEventAlibabaCloudActionTrail.yaml

## Version 0.1.1 - 2026-09-14

- (2026-09-14) Support IPv6 prefixes in srcipaddr_has_any_prefix, and short-circuit newvalue_has_any since NewValue isn't populated by this source

## Version 0.1.0 - 2026-09-14

- (2026-09-14) Initial creation of the parser
- Adds filtering parameters (starttime, endtime, srcipaddr_has_any_prefix, eventtype_in, eventresult, actorusername_has_any, operation_has_any, object_has_any, newvalue_has_any) to ASimAuditEventAlibabaCloudActionTrail for improved query performance
