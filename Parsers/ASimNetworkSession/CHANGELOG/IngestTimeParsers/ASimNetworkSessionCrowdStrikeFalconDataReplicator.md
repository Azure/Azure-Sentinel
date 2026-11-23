# Changelog for ASimNetworkSessionCrowdStrikeFalconDataReplicator.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `CrowdStrike_Network_Events_CL NetworkSession ASIM parser`.

## Version 0.1.0

- (2026-10-28) Add the ingestion-time CrowdStrike Falcon Data Replicator NetworkSession parser - [PR #15457](https://github.com/Azure/Azure-Sentinel/pull/15457)
- Retain explicit packed fields and endpoint direction precedence from the query-time parser.
