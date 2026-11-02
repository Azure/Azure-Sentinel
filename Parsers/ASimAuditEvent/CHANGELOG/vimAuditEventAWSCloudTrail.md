# Changelog for vimAuditEventAWSCloudTrail.yaml

## Version 0.2.0

- (2026-11-02) Replaced the monolithic query with a filtering fuzzy union of 16 EC2 action parsers covering 810 actions and AuditEvent schema 1.0.0. - [PR #15531](https://github.com/Azure/Azure-Sentinel/pull/15531)

## Version 0.1.0
- (2026-02-17) [ASIM] AuditEvent - AWS Cloud Trail (New Parser) - [PR #13428](https://github.com/Azure/Azure-Sentinel/pull/13428)
- Create parser for AWSCloudTrail
- Support the following EventSources: ec2.amazonaws.com

