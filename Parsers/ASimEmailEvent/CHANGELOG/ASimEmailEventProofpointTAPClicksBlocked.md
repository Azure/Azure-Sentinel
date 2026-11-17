# Changelog for ASimEmailEventProofpointTAPClicksBlocked.yaml

## Version 0.1.0

- (2026-10-30) Added Proofpoint TAP blocked-click normalization as EmailEvent interaction activity - [PR #15530](https://github.com/Azure/Azure-Sentinel/pull/15530)
- Preserve one event per source row and require the source id directly for EventOriginalUid.
- Retain clicksBlocked and the original blocking action without asserting email delivery or delivery failure.
- Map click timing, recipient, sender, URL, and threat context; optionally pack the remaining message and campaign metadata.
