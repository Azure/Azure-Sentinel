# Changelog for vimAlertEventAWSGuardDuty

## Version 0.1.0 - 2026-09-09

- (2026-09-09) Initial creation of the filtering parser - [PR #15079](https://github.com/Azure/Azure-Sentinel/pull/15079)
- Added AlertEvent time, entity, ATT&CK tactic, threat category, and severity filters
- Ensured `ThreatRiskLevel` is emitted as an integer
- Documented handling of unsupported technique and verdict filters
- Preserved source resource and service details through the optional `pack` parameter
