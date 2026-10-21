# Changelog for ASimProcessEventCrowdStrikeFalconEndpointProtection.yaml

## Version 0.1.0

- (2026-10-21) Added CrowdStrike Falcon Endpoint Protection normalization from CrowdStrike_Process_Events_CL to ProcessEvent 1.0.0.
- Supports process rollups, synthetic observations, process end events, and termination requests without event correlation or row expansion.
- Maps native OS process IDs only when attributable; preserves Falcon correlation IDs and unmapped source fields with pack=true.
