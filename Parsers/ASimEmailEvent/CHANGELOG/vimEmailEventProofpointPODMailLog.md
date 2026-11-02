# Changelog for vimEmailEventProofpointPODMailLog.yaml

## Version 0.1.3

- (2026-10-30) Read Proofpoint MailLog event IDs directly from the source `id` column - [PR #15463](https://github.com/Azure/Azure-Sentinel/pull/15463)
- Use the declared source column to populate `EventOriginalUid` without changing filtering.

## Version 0.1.2

- (2026-10-24) Normalize mailbox-form relay hosts and identify relay-less local delivery destinations - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Preserve filtering while extracting the relay host and using the reporting device for local delivery without a relay endpoint.

## Version 0.1.1

- (2026-10-23) Handle missing optional source IDs in CI-ingested records without changing filtering or inventing event identifiers - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Register the current CCP table schema in the KQL validation catalog.

## Version 0.1.0

- (2026-10-21) Added a Proofpoint POD MailLog EmailEvent filtering parser with time, IPv4 prefix, direction and result filters - [PR #15410](https://github.com/Azure/Azure-Sentinel/pull/15410)
- Nonempty header sender, header recipient, subject and delivery-location filters return no rows because these fields are unavailable.
- Live schema, data and filter validation are deferred.
