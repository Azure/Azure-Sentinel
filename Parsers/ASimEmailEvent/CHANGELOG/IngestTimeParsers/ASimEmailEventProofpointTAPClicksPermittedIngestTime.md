# Changelog for ASimEmailEventProofpointTAPClicksPermittedIngestTime.yaml

## Version 0.1.3

- (2026-10-30) Read the source id directly for EventOriginalUid without a missing-column fallback, matching the query-time parsers - [PR #15501](https://github.com/Azure/Azure-Sentinel/pull/15501)
- Require the declared source id column; retain one normalized event per source row and all other mappings.

## Version 0.1.2

- (2026-10-29) Added the initial Proofpoint TAP permitted-click ingestion-time parser for EmailEvent interaction activity - [PR #15501](https://github.com/Azure/Azure-Sentinel/pull/15501)
- Normalize each source row into ASimEmailEventLogs while preserving the original click type, optional event identifier, click-time fallback, and threat context.
- Retain campaign, message, sender IP, threat status, and user-agent context in AdditionalFields.
