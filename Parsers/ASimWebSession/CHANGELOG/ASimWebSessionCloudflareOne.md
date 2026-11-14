# Changelog for ASimWebSessionCloudflareOne.yaml

## Version 0.1.1

- (2026-11-13) Preserve configured Cloudflare collector account identity in ASIM device scope fields - [PR #15659](https://github.com/Azure/Azure-Sentinel/pull/15659)
- Map `CloudflareAccountId` and `CloudflareAccountName` to `DvcScopeId` and `DvcScope`; fall back to source `AccountID` when configured account attribution is absent.

## Version 0.1.0

- (2026-09-30) Cloudflare One Web Session Parser - [PR #14982](https://github.com/Azure/Azure-Sentinel/pull/14982)

