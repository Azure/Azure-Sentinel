# Changelog for ASimAuditEventAWSCloudTrail.yaml

## Version 0.2.0

- (2026-11-02) Replace the monolithic EC2 query with a fuzzy union of the 16 EC2 action-family parsers. - [PR #15531](https://github.com/Azure/Azure-Sentinel/pull/15531)
- Forward disabled and pack to every child parser and declare the corresponding built-in parser dependencies.
- Use AuditEvent schema version 1.0.0 to match the child parsers and expose their 810 documented EC2 API actions and entity placeholders.

## Version 0.1.0
- (2026-02-17) [ASIM] AuditEvent - AWS Cloud Trail (New Parser) - [PR #13428](https://github.com/Azure/Azure-Sentinel/pull/13428)
- Create parser for AWSCloudTrail
- Support the following EventSources: ec2.amazonaws.com
