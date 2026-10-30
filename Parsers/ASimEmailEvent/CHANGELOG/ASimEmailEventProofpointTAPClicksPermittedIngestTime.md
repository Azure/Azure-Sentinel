# Changelog for ASimEmailEventProofpointTAPClicksPermittedIngestTime.yaml

## Version 0.1.2

- (2026-10-29) Added the initial Proofpoint TAP permitted-click ingestion-time parser for EmailEvent interaction activity - [PR #15501](https://github.com/Azure/Azure-Sentinel/pull/15501)
- Normalize each source row into ASimEmailEventLogs while preserving the original click type, optional event identifier, click-time fallback, and threat context.
- Retain campaign, message, sender IP, threat status, and user-agent context in AdditionalFields.
