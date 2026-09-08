# Changelog for ASimAlertEventWizCloud.yaml

## Version 0.1.1

- (2026-09-08) Updating parser to align with the update of the Alert Event schema to version 1.0.0 as part of [PR #14628]
(https://github.com/Azure/Azure-Sentinel/pull/14628)
    - Added `UserEntityKey` (mapped from `UserId`) and `DvcEntityKey` (mapped from `DvcId`)


## Version 0.1.0

- (2026-08-31) Initial creation of the parser
    - Normalizes Wiz Cloud issues (`WizIssuesV3_CL`). Vendor/product are `Wiz`/`Cloud`, distinct from the sibling `ASimAlertEventWizDefend` (`Wiz`/`Defend`) parser for `WizDetectionsV3_CL`