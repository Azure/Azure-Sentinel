# Changelog for ASimDnsCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.0

- (2026-10-23) Initial DNS parser for CrowdStrike Falcon Data Replicator events in `CrowdStrike_DNS_Events_CL` - [PR #15417](https://github.com/Azure/Azure-Sentinel/pull/15417)
- Uses populated `event_simpleName` values to select DNS events and includes mappings for currently empty columns.
- Preserves unverified vendor metadata with `pack=true`, without event enrichment or row expansion.