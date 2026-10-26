# Changelog for vimNetworkSessionCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.0

- (2026-10-26) Initial creation of the CrowdStrike Falcon Data Replicator Network Session filtering parser for CrowdStrike_Network_Events_CL.
- Apply inclusive TimeGenerated bounds, IPv4 address-prefix, destination-port, action, result, and disabled filters.
- Set ASimMatchingIpAddr to the matched endpoint role; nonempty hostname filters return no records because the source has no hostname column.
- Preserve the parameterless parser mappings, entity placeholders, and opt-in packing of source-only fields and undocumented action codes.
