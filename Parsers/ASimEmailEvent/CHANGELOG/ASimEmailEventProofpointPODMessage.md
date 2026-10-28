# Changelog for ASimEmailEventProofpointPODMessage.yaml

## Version 0.1.2

- (2026-10-28) Add the ingestion-time EmailEvent parser and source-table-specific fixture for Proofpoint POD messages - [PR #15464](https://github.com/Azure/Azure-Sentinel/pull/15464)
- (2026-10-23) Validate Proofpoint connection hosts before mapping ASIM source hostname and domain fields - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Retain valid single-label hostnames; leave IP-shaped, malformed, and non-FQDN values out of SrcFQDN and SrcDomain.

## Version 0.1.1

- (2026-10-23) Map observed DMARC outcomes and message dispositions case-insensitively - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Map quarantine/reject DMARC outcomes to Fail and preserve the DMARC policy; retain unsupported error results in EmailDmarcOriginalResult.
- Map hold to Quarantined and redirect to Redirected without treating filter acceptance as delivery confirmation.

## Version 0.1.0

- (2026-10-21) Added the initial ProofpointPODMessage_CL EmailEvent inspection parser - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Preserves message cardinality and recipient arrays; filter continuation does not imply delivery success.
- Adds opt-in source details through `pack` and empty schema-defined entity placeholders.
