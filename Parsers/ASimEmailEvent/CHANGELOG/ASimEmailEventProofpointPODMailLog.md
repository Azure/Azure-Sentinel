# Changelog for ASimEmailEventProofpointPODMailLog.yaml

## Version 0.1.3

- (2026-10-30) Read the Proofpoint source ID directly instead of substituting an empty value for a missing column - [PR #15512](https://github.com/Azure/Azure-Sentinel/pull/15512)
- Preserve connector-provided IDs; CI replay that omits `id` is expected to fail QTP execution until fixture tooling is corrected.

## Version 0.1.2

- (2026-10-24) Normalize mailbox-form relay hosts and identify relay-less local delivery destinations - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Extract the host from relay values such as `pps@localhost`; use the reporting device as destination only when `sm.mailer=local` and no relay endpoint is available.

## Version 0.1.1

- (2026-10-23) Handle missing optional source IDs in CI-ingested records while preserving connector-provided IDs - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Register the current CCP table schema in the KQL validation catalog.

## Version 0.1.0

- (2026-10-21) Added a Proofpoint POD MailLog EmailEvent parser using the CCP table schema and repository samples - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Preserves individual SMTP receipt and delivery records without correlation or recipient expansion.
- Live schema and data validation are deferred.
