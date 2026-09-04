# Changelog for ASimAlertEventAWSGuardDuty

## Version 0.1.1 - 2026-09-04

- (2026-09-04) Ensured `ThreatRiskLevel` is emitted as an integer

## Version 0.1.0 - 2026-09-02

- (2026-09-02) Initial creation of the parser
- Normalized GuardDuty finding identity, severity, lifecycle, resource, user, action, and threat context
- Preserved source resource and service details through the optional `pack` parameter
