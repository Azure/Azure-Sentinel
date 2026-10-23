# Changelog for ASimUserManagementAWSCloudTrail.yaml

## Version 0.1.1

- (2026-10-23) Remove the duplicate IAM lookup entry for UntagUser so each matching event produces one UserModified output row. - [PR #15408](https://github.com/Azure/Azure-Sentinel/pull/15408)
- Remove the trailing semicolon from the parser invocation so callers and KQL validation can append pipeline operators.

## Version 0.1.0
- (2026-01-26) [ASIM] UserManagement - AWSCloudTrail (New Parser) - [PR #13503](https://github.com/Azure/Azure-Sentinel/pull/13503)
- Create parser for AWSCloudTrail
- Support the following EventSources: cognito-idp.amazonaws.com, iam.amazonaws.com