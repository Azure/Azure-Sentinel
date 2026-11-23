# Changelog for ASimAuditEventCrowdStrikeFalconDataReplicator.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged.
- Rename the display name to `CrowdStrike_Audit_Events_CL AuditEvent ASIM parser`.

## Version 0.1.1

- (2026-11-06) Reduce ingestion transform size by removing redundant mappings - [PR #15577](https://github.com/Azure/Azure-Sentinel/pull/15577)
- The removed EventType and ObjectType branches returned the existing `Other` fallback.

## Version 0.1.0

- (2026-10-28) Add the ingestion-time CrowdStrike Falcon Data Replicator AuditEvent parser - [PR #15450](https://github.com/Azure/Azure-Sentinel/pull/15450)
