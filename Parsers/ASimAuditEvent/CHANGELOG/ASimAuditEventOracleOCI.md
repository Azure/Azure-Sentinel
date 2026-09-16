# Changelog for ASimAuditEventOracleOCI.yaml

## Version 0.1.1

- (2026-09-14) Added compartment OCID as a fallback for the mandatory `Object` field, so read-only List* operations (which act on a compartment scope rather than a single resource) no longer leave it empty.

## Version 0.1.0

- (2026-09-14) First commit
