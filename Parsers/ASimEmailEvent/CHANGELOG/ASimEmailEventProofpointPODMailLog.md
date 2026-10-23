# Changelog for ASimEmailEventProofpointPODMailLog.yaml

## Version 0.1.1

- (2026-10-23) Handle missing optional source IDs in CI-ingested records while preserving connector-provided IDs - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Register the current CCP table schema in the KQL validation catalog.

## Version 0.1.0

- (2026-10-21) Added a Proofpoint POD MailLog EmailEvent parser using the CCP table schema and repository samples - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Preserves individual SMTP receipt and delivery records without correlation or recipient expansion.
- Live schema and data validation are deferred.
