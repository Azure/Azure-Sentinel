# Changelog for ASimAuditEventBarracudaWAF.yaml

## Version 0.2.3

- (2026-10-10) Exclude SESSION_TIMEOUT events now normalized by the Authentication parser. - [PR #15298](https://github.com/Azure/Azure-Sentinel/pull/15298)
- Align the declared and output schema version with 1.0.0; use an explicit normalized output projection and add the required entity placeholders.
- Document accepted missing-field warnings in the YAML Exceptions section.
- Populate EventUid from _ItemId when available, leaving exported records without an ingestion ID empty.

## Version 0.2.2

- (2026-10-05) Normalize the ASIM schema version to 0.1.0 - [PR #15265](https://github.com/Azure/Azure-Sentinel/pull/15265)

## Version 0.2.1

- (2024-07-16) ASimAuditEventBarracudaWAF.yaml-2 - [PR #10641](https://github.com/Azure/Azure-Sentinel/pull/10641)

## Version 0.1

- (2023-08-01) ASIM Audit schema parser with its sample and test data for Barracuda - [PR #8332](https://github.com/Azure/Azure-Sentinel/pull/8332)

