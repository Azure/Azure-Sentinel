# Changelog for ASimAuditEventCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.0

- (2026-10-23) Initial creation of the CrowdStrike Falcon Data Replicator AuditEvent parser - [PR #15414](https://github.com/Azure/Azure-Sentinel/pull/15414)
- Normalize 45 source event names using event_simpleName only; do not use the versioned name as a fallback.
- Account for all 113 source columns, including currently empty columns; retain original fields with pack=true.
- Preserve unknown numeric enumerations without inventing meanings and leave unavailable device and object values empty.
- Use an explicit output projection and preserve one output record per accepted input record.
- Tolerate absent ingestion metadata columns while retaining the declared source table in Type.
