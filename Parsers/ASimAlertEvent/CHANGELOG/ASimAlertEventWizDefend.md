# Changelog for ASimAlertEventWizDefend.yaml

## Version 0.1.1

- (2026-09-08) Updating parser to align with the update of the Alert Event schema to version 1.0.0 as part of [PR #14628](https://github.com/Azure/Azure-Sentinel/pull/14628)
    - Added `UserEntityKey` (mapped from `UserId`), `DvcEntityKey` (mapped from `DvcId`), `ProcessEntityKey` (mapped from `ProcessId`), and `FileEntityKey` (mapped from `FileSHA1`)
    - `AttackTactics` is now mapped from the raw MITRE tactic IDs to tactic names (e.g. `Privilege Escalation` instead of `TA0004`), matching the ASIM schema's preferred format and the convention used by other AlertEvent parsers. `AttackTechniques` remains ID-only, as there is no reliable technique ID-to-name mapping available.


## Version 0.1.0

- (2026-08-31) Initial creation of the parser
    - Normalizes Wiz Defend threat detections (`WizDetectionsV3_CL`). Vendor/product stay `Wiz`/`Defend` regardless of the underlying `tdrSource` (WIZ, WIZ_SENSOR, GUARD_DUTY)
