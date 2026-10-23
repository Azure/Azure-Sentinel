# Changelog for vimEmailEventProofpointPODMessage.yaml

## Version 0.1.0

- (2026-10-21) Added the filtering ProofpointPODMessage_CL EmailEvent inspection parser - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- (2026-10-23) Normalize JSON-encoded dynamic objects before applying field filters - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Adds time, IPv4 prefix, sender, To-recipient, subject, direction and result filters before remaining normalization.
- Nonempty delivery-location filters return no rows because message inspection does not establish delivery location.
- Live source sampling and schema/data/filter validation are deferred by user direction.
