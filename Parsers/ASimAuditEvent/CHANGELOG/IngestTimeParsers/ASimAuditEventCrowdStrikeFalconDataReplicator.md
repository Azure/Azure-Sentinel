# Changelog for ASimAuditEventCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.1

- (2026-11-06) Reduce ingestion transform size by removing redundant mappings - [PR #15577](https://github.com/Azure/Azure-Sentinel/pull/15577)
- The removed EventType and ObjectType branches returned the existing `Other` fallback.
- This history applies only to the [ingestion-time parser](../../IngestTimeParsers/ASimAuditEventCrowdStrikeFalconDataReplicator.yaml). The [query-time parser history](../ASimAuditEventCrowdStrikeFalconDataReplicator.md) is maintained separately.

## Version 0.1.0

- (2026-10-28) Add the ingestion-time CrowdStrike Falcon Data Replicator AuditEvent parser - [PR #15450](https://github.com/Azure/Azure-Sentinel/pull/15450)
