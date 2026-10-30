# Changelog for ASimEmailEventProofpointPODMailLog.yaml

## Version 0.1.4

- (2026-10-30) Normalize relay hosts using a positive last-component index and anchored extraction - [PR #15512](https://github.com/Azure/Azure-Sentinel/pull/15512)
- Preserve the last `@` component and remove trailing dots before source and destination mapping; leave relay IPs, delivery classification, UID mappings, filtering, and the raw `sm` bag unchanged.

## Version 0.1.3

- (2026-10-30) Normalize missing envelope recipients before filtering and delivery classification - [PR #15463](https://github.com/Azure/Azure-Sentinel/pull/15463)
- Treat an absent `sm["to"]` value as an empty dynamic array for both filtering and delivery classification, while preserving the original `sm` bag in `AdditionalFields`.

## Version 0.1.2

- (2026-10-28) Add the ingestion-time EmailEvent parser and source-table-specific fixture for Proofpoint POD MailLog - [PR #15463](https://github.com/Azure/Azure-Sentinel/pull/15463)
