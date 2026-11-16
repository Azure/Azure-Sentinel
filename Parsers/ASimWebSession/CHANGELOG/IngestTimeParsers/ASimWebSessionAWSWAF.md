# Changelog for ASimWebSessionAWSWAF.yaml

## Version 0.1.0

- (2026-11-13) Initial ingestion-time conversion of ASimWebSessionAWSWAF for the AWS S3 WAF CCF connector and ASimWebSessionLogs destination.
- Parses HTTP headers with four regex operations: one property-order rewrite, two bulk extractions, and one five-key `parse-kv` operation, without row expansion or aggregation.
- Normalizes only header names and preserves the first nonempty value. Captured JSON string literals are decoded twice after `zip` serialization to retain value casing and escaping.
- Retains HttpCookie and HttpRequestHeaderCount in AdditionalFields alongside the existing AWS fields.
- Preserves source device identifiers and projects physical destination columns without query-time-only aliases.
