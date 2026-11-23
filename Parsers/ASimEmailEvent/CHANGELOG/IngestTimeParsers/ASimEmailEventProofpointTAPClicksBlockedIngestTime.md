# Changelog for ASimEmailEventProofpointTAPClicksBlockedIngestTime.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `ProofPointTAPClicksBlockedV2_CL EmailEvent ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.0

- (2026-11-04) Added the initial Proofpoint TAP blocked-click ingestion-time EmailEvent parser - [PR #15553](https://github.com/Azure/Azure-Sentinel/pull/15553)
- Preserve one EmailInteraction per source row, direct source identifiers, original blocking action, timestamp fallback, and threat context without inferring an email delivery outcome.
- Retain campaign, message, sender IP, threat status, and user-agent context in AdditionalFields.
- Expect the connector-prepared raw-table shape, including TimeGenerated; preparation composition and native destination acceptance require separate validation.
