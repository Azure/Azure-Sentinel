# Changelog for ASimEmailEventProofpointTAPClicksPermitted.yaml

## Version 0.1.0

- (2026-10-28) Added Proofpoint TAP permitted-click normalization as EmailEvent inspection activity - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Preserve one event per source row and retain the original click type without asserting email delivery or HTTP success.
- Map click timing, recipient, sender, and threat context; optionally pack message identifiers, campaign, sender IP, original threat status, and user agent.
