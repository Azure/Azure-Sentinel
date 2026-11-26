# Changelog for ASimFileEventCrowdStrikeFalconDataReplicator.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `CrowdStrike_File_Events_CL FileEvent ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.0

- (2026-10-29) Add the ingestion-time CrowdStrike Falcon Data Replicator FileEvent parser - [PR #15455](https://github.com/Azure/Azure-Sentinel/pull/15455)
- Retain nested source packing and literal path replacements from the query-time parser.
