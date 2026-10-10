# Changelog for vimAuthenticationBarracudaWAF.yaml

## Version 0.1.3

- (2026-10-10) Normalize SESSION_TIMEOUT as a successful Logoff with Session expired result details. - [PR #15298](https://github.com/Azure/Azure-Sentinel/pull/15298)
- Align the declared and output schema version with 1.0.0; use an explicit normalized output projection and add the required entity placeholders.
- Apply the eventresult filter to CommonSecurityLog events, including session timeouts.
- Document accepted missing-field warnings in the YAML Exceptions section.
- Populate EventUid from _ItemId when available, leaving exported records without an ingestion ID empty.

## Version 0.1.2

- (2024-06-19) april entity mapping updates diana p3 - [PR #10342](https://github.com/Azure/Azure-Sentinel/pull/10342)
- (2024-04-19) Authentication parser filter update - [PR #10243](https://github.com/Azure/Azure-Sentinel/pull/10243)

## Version 0.1

- (2023-08-01) ASIM Authentication schema parser with its sample and test data for Barracuda WAF - [PR #8333](https://github.com/Azure/Azure-Sentinel/pull/8333)

