# Changelog for vimDnsCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.0

- (2026-10-23) Initial filtering DNS parser for CrowdStrike Falcon Data Replicator - [PR #15417](https://github.com/Azure/Azure-Sentinel/pull/15417)
- Supports inclusive `TimeGenerated` boundaries, domain matching, IPv4 answer and prefix filters, response codes, event types, disabling, and optional vendor metadata packing.
- Retains the same record-local mappings and normalization boundaries as the parameterless parser.
