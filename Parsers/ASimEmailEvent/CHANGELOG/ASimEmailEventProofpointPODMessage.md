# Changelog for ASimEmailEventProofpointPODMessage.yaml

## Version 0.1.0

- (2026-10-21) Added the initial ProofpointPODMessage_CL EmailEvent inspection parser.
- Preserves message cardinality and recipient arrays; filter continuation does not imply delivery success.
- Adds opt-in source details through `pack` and empty schema-defined entity placeholders.
