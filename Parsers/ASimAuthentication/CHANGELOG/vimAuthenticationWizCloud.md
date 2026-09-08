# Changelog for vimAuthenticationWizCloud.yaml

## Version 0.1.1

- (2026-09-08) Updating parser to align with the update of the Authentication  schema to version 1.0.0 as part of [PR #14628](https://github.com/Azure/Azure-Sentinel/pull/14628)
    - Added `TargetUserEntityKey` (mapped from `TargetUserId`)


## Version 0.1.0

- (2026-08-31) Initial creation of the parser
    - Only the `Login` and `TokenRefresh` audit actions are mapped, since the source table also carries unrelated non-authentication API action types
    - `srchostname_has_any`, `targetappname_has_any`, and `eventresultdetails_in` are accepted for compatibility with the imAuthentication unifying parser's parameter set but are not functional for this source
