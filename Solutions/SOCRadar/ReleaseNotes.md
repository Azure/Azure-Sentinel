# SOCRadar for Microsoft Sentinel - Release Notes

## Version 3.0.0 (February 2026)

### Initial Release

- SOCRadar-Alarm-Import playbook (v3.29.0)
  - Pagination support for large alarm volumes
  - Duplicate detection via Sentinel API
  - Three-tag system: SOCRadar + alarm_main_type + alarm_sub_type
  - Field truncation for Sentinel description limits
  - Optional audit logging to Log Analytics
  - ImportAllStatuses parameter for flexible filtering
  - 3-minute delayed start for role propagation

- SOCRadar-Alarm-Sync playbook (v2.9.0)
  - Classification mapping (FalsePositive, BenignPositive, TruePositive)
  - Severity sync back to SOCRadar
  - Synced tag for deduplication
  - Pagination for 1000+ incidents

- SOCRadar Integration Dashboard workbook
  - Alarm severity distribution
  - Alarm timeline
  - Top alarm types
  - Audit log monitoring

- 5 Hunting Queries
  - Alarm overview, critical alarms, trends, incident correlation, audit analysis
