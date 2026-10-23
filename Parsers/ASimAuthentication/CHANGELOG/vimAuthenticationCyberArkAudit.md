# Changelog for vimAuthenticationCyberArkAudit.yaml

## Version 0.1.0

- (2026-10-05) Initial creation of the parser
    - Maps Identity logins, Vault logons, PSM sessions, SIA/DPA RDP sessions and SSH sessions; IDP2013/IDP2014 MFA challenge events are excluded
    - For session events, the Actor is the initiating user and the Target is the privileged account
    - Identity `EventStartTime`/`EventEndTime` use the UTC `when_occurred` value, falling back to `TimeGenerated`
    - [PR #15262](https://github.com/Azure/Azure-Sentinel/pull/15262)
