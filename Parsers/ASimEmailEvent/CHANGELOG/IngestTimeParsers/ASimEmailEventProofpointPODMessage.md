# Changelog for ASimEmailEventProofpointPODMessage.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `ProofpointPODMessage_CL EmailEvent ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.2

- (2026-10-28) Add the ingestion-time EmailEvent parser and source-table-specific fixture for Proofpoint POD messages - [PR #15464](https://github.com/Azure/Azure-Sentinel/pull/15464)
- This history applies only to the [ingestion-time parser](../../IngestTimeParsers/ASimEmailEventProofpointPODMessage.yaml). The [query-time parser history](../ASimEmailEventProofpointPODMessage.md) is maintained separately.
