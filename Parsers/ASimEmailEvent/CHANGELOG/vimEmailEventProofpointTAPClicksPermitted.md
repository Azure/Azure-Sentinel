# Changelog for vimEmailEventProofpointTAPClicksPermitted.yaml

## Version 0.1.0

- (2026-10-28) Added the filtering Proofpoint TAP permitted-click EmailEvent parser.
- Apply event-time, clicker IPv4-prefix, recipient, direction, result, and disable filters before normalization.
- Retain empty-parameter checks for unavailable header From, subject, and delivery location; preserve the parameterless parser's mappings and packing controls.
