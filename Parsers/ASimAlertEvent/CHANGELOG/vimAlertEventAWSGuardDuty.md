# Changelog for vimAlertEventAWSGuardDuty

## Version 0.1.1 - 2026-09-04

- (2026-09-04) Ensured `ThreatRiskLevel` is emitted as an integer
- (2026-09-04) Prevented unsupported technique and verdict filters from excluding all events

## Version 0.1.0 - 2026-09-02

- (2026-09-02) Initial creation of the filtering parser
- Added AlertEvent time, entity, ATT&CK, threat category, verdict, and severity filters
- Preserved source resource and service details through the optional `pack` parameter
