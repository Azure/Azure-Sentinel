# Changelog for vimEmailEventProofpointTAPClicksBlocked.yaml

## Version 0.1.0

- (2026-10-30) Added the filtering Proofpoint TAP blocked-click EmailEvent parser - [PR #15530](https://github.com/Azure/Azure-Sentinel/pull/15530)
- Apply event-time, clicker IPv4-prefix, recipient, direction, result, and disable filters before normalization.
- Retain empty-parameter checks for unavailable header From, subject, and delivery location.
- Preserve the parameterless parser's mappings, source identifiers, cardinality, and optional packing.
