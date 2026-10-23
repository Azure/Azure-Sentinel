# Changelog for ASimEmailEventProofpointPODMessage.yaml

## Version 0.1.0

- (2026-10-21) Added the initial ProofpointPODMessage_CL EmailEvent inspection parser - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- (2026-10-23) Normalize JSON-encoded dynamic objects before mapping nested fields - [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409)
- Preserves message cardinality and recipient arrays; filter continuation does not imply delivery success.
- Adds opt-in source details through `pack` and empty schema-defined entity placeholders.
