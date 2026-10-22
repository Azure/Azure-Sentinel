# Changelog for vimEmailEventProofpointPODMessage.yaml

## Version 0.1.0

- (2026-10-21) Added the filtering ProofpointPODMessage_CL EmailEvent inspection parser.
- Adds time, IPv4 prefix, sender, To-recipient, subject, direction and result filters before remaining normalization.
- Nonempty delivery-location filters return no rows because message inspection does not establish delivery location.
- Live source sampling and schema/data/filter validation are deferred by user direction.
