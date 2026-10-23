# Changelog for vimUserManagementAWSCloudTrail.yaml

## Version 0.1.1

- (2026-10-23) Remove the duplicate IAM lookup entry for UntagUser so each matching event produces one UserModified output row.

## Version 0.1.0
- (2026-01-26) [ASIM] UserManagement - AWSCloudTrail (New Parser) - [PR #13503](https://github.com/Azure/Azure-Sentinel/pull/13503)
- Create parser for AWSCloudTrail
- Support the following EventSources: cognito-idp.amazonaws.com, iam.amazonaws.com