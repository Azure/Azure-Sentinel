# Changelog for ASimAlertEventAWSGuardDuty

## Version 0.1.0 - 2026-09-09

- (2026-09-09) Initial creation of the parser - [PR #15079](https://github.com/Azure/Azure-Sentinel/pull/15079)
- Normalized GuardDuty finding identity, severity, lifecycle, resource, user, action, and threat context
- Ensured `ThreatRiskLevel` is emitted as an integer
- Preserved source resource and service details through the optional `pack` parameter
