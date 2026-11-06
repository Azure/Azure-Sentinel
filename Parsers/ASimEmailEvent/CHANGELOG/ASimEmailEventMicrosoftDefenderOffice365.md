# Changelog for ASimEmailEventMicrosoftDefenderOffice365.yaml

## Version 0.1.0

- (2026-10-26) Add native Microsoft Defender for Office 365 EmailEvent normalization - [PR #15430](https://github.com/Azure/Azure-Sentinel/pull/15430)
- Preserve individual source records and keep delivery results separate from threat verdicts.
- Map the known To/Cc arrays directly, normalize null arrays to empty, and explicitly pack unmapped source fields.
