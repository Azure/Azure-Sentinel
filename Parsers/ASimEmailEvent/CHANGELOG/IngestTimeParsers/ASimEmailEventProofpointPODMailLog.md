# Changelog for ASimEmailEventProofpointPODMailLog.yaml

## Version 0.1.4

- (2026-11-06) Validate relay IP addresses inline without native IP functions or top-level helpers - [PR #15572](https://github.com/Azure/Azure-Sentinel/pull/15572)
- Keep the transformation source-rooted and preserve valid IPv4, full/compressed IPv6, and IPv4-embedded IPv6 literals in the existing source/destination mappings.
- Reject malformed addresses, CIDR prefixes, zone identifiers, and surrounding whitespace. Validate embedded IPv4 octets before counting them as two IPv6 groups.
- Use the existing transformation-compatible `replace` function for the validation copy; live validation rejected `replace_regex`.
- Validated KQL syntax/semantics and address handling locally; the regression harness is not included in the PR. Live DCR compilation and enablement have not been attempted.

## Version 0.1.3

- (2026-10-30) Normalize missing envelope recipients before filtering and delivery classification - [PR #15463](https://github.com/Azure/Azure-Sentinel/pull/15463)
- Treat an absent `sm["to"]` value as an empty dynamic array for both filtering and delivery classification, while preserving the original `sm` bag in `AdditionalFields`.

## Version 0.1.2

- (2026-10-28) Add the ingestion-time EmailEvent parser and source-table-specific fixture for Proofpoint POD MailLog - [PR #15463](https://github.com/Azure/Azure-Sentinel/pull/15463)
