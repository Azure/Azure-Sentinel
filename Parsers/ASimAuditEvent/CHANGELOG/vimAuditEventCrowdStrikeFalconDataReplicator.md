# Changelog for vimAuditEventCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.0

- (2026-10-23) Initial creation of the CrowdStrike Falcon Data Replicator AuditEvent filtering parser - [PR #15414](https://github.com/Azure/Azure-Sentinel/pull/15414)
- Add TimeGenerated bounds, IPv4 source-address prefixes, event type and result, actor, operation, object, and new-value filters.
- Preserve parameterless normalization and support disabled and pack controls.
- Apply source-column filters before parsing and object/new-value filters before optional packing.
- Tolerate absent ingestion metadata columns while retaining the declared source table in Type.
