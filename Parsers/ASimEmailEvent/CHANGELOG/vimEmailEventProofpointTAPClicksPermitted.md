# Changelog for vimEmailEventProofpointTAPClicksPermitted.yaml

## Version 0.1.2

- (2026-10-29) Read the optional source id defensively while retaining the existing filtering behavior - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Preserve real identifiers when present; leave EventOriginalUid empty when the source id is absent without fabricating a replacement.

## Version 0.1.1

- (2026-10-28) Classify filtered permitted URL clicks as EmailInteraction using the new EmailEvent event type - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Preserve clicksPermitted as the original event type and retain the existing filtering, mappings, and packing behavior.

## Version 0.1.0

- (2026-10-28) Added the filtering Proofpoint TAP permitted-click EmailEvent parser - [PR #15483](https://github.com/Azure/Azure-Sentinel/pull/15483)
- Apply event-time, clicker IPv4-prefix, recipient, direction, result, and disable filters before normalization.
- Retain empty-parameter checks for unavailable header From, subject, and delivery location; preserve the parameterless parser's mappings and packing controls.
