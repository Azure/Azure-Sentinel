# Changelog for vimEmailEventProofpointPODMessage.yaml

## Version 0.1.2

- (2026-10-23) Match the parameterless parser's validated Proofpoint connection-host mapping - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Keep valid single-label hostnames and avoid classifying IP-shaped or malformed host values as ASIM FQDNs.

## Version 0.1.1

- (2026-10-23) Match the parameterless parser's DMARC and disposition mappings - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Map quarantine/reject DMARC outcomes to Fail and preserve the DMARC policy; retain unsupported error results in EmailDmarcOriginalResult.
- Map hold to Quarantined and redirect to Redirected; filtering behavior is unchanged.

## Version 0.1.0

- (2026-10-21) Added the filtering ProofpointPODMessage_CL EmailEvent inspection parser - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Adds time, IPv4 prefix, sender, To-recipient, subject, direction and result filters before remaining normalization.
- Nonempty delivery-location filters return no rows because message inspection does not establish delivery location.
- Live source sampling and schema/data/filter validation are deferred by user direction.
