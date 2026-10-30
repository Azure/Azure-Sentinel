# Changelog for ASimEmailEventProofpointTAPBlocked.yaml

## Version 0.1.0

- (2026-10-29) Initial Proofpoint TAP messages-blocked parser for ASIM EmailEvent 1.0.0 - [PR #15500](https://github.com/Azure/Azure-Sentinel/pull/15500)
- Map prevented delivery to Failure, device action to Quarantined, and delivery location to Quarantine.
- Retain the original quarantine folder and rule while preserving one normalized row per source row.
