# Changelog for ASimEmailEventProofpointTAPClicksPermitted.yaml

## Version 0.1.2

- (2026-10-29) Read the optional source id defensively so a missing column does not prevent event normalization - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Preserve real identifiers when present; leave EventOriginalUid empty when the source id is absent without fabricating a replacement.

## Version 0.1.1

- (2026-10-28) Classify permitted URL clicks as EmailInteraction using the new EmailEvent event type - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Preserve clicksPermitted as the original event type, all existing mappings, and one normalized event per source row.

## Version 0.1.0

- (2026-10-28) Added Proofpoint TAP permitted-click normalization as EmailEvent inspection activity - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Preserve one event per source row and retain the original click type without asserting email delivery or HTTP success.
- Map click timing, recipient, sender, and threat context; optionally pack message identifiers, campaign, sender IP, original threat status, and user agent.
