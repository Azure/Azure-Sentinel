# Changelog for vimEmailEventProofpointPODMailLog.yaml

## Version 0.1.0

- (2026-10-21) Added a Proofpoint POD MailLog EmailEvent filtering parser with time, IPv4 prefix, direction and result filters.
- Nonempty header sender, header recipient, subject and delivery-location filters return no rows because these fields are unavailable.
- Live schema, data and filter validation are deferred. No pull request has been created for this change.
