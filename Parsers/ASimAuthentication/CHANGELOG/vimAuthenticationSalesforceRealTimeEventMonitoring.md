# Changelog for vimAuthenticationSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0

- (2026-10-26) Initial creation of the parser
- Maps LoginEvent, LoginAsEvent, LogoutEvent and IdentityVerificationEvent from SalesForceRealTimeEventMonitoring_CL
- LoginAsEvent is mapped as EventSubType AssumeRole with the impersonating admin as Actor
- IdentityVerificationEvent step-up verifications for actions other than login are mapped as EventType Elevate
- Converts the hex-encoded SourceIp of IdentityVerificationEvent to a regular IP address
- TargetSessionId uses LoginKey so Logon and Logoff events of a session correlate
- Blocking or failed transaction security PolicyOutcome values override the event status and map to EventResult Failure
- IdentityVerificationEvent Initiated and InProgress statuses are mapped to EventResult NA
