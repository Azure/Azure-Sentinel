# Changelog for vimAuthenticationCrowdStrikeFalcon.yaml

## Version 0.1.0

- (2026-10-23) Initial CrowdStrike Falcon Data Replicator Authentication filtering parser for CrowdStrike_Auth_Events_CL.
- Support time, source IPv4 prefix or exact IP, source hostname, username, event type, result, and result-detail filtering.
- Return no events for a nonempty target application filter because the source has no target application name.
- Preserve the parameterless parser mappings and optional original-source packing.
