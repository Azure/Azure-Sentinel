# Changelog for ASimAuthenticationCrowdStrikeFalcon.yaml

## Version 0.1.0

- (2026-10-23) Initial CrowdStrike Falcon Data Replicator Authentication parser for CrowdStrike_Auth_Events_CL.
- Normalize supported logon, failed logon, and logoff events, including versioned event-name fallbacks.
- Map available identity, device, address, protocol, and session fields, including columns empty in the initial source sample.
- Preserve all original columns with pack=true without decoding undocumented flags or status codes.
