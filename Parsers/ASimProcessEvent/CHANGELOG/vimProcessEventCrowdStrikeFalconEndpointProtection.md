# Changelog for vimProcessEventCrowdStrikeFalconEndpointProtection.yaml

## Version 0.1.1

- (2026-10-29) Replaced the all-column source snapshot with unconditional explicit pack() of unnormalized columns in AdditionalFields immediately before the final projection.
- Preserves the original Falcon TargetProcessId and nests source AdditionalFields under SourceAdditionalFields.

## Version 0.1.0

- (2026-10-21) Added parameterized CrowdStrike Falcon Endpoint Protection normalization from CrowdStrike_Process_Events_CL to ProcessEvent 1.0.0 - [PR #15391](https://github.com/Azure/Azure-Sentinel/pull/15391)
- Supports standard ProcessEvent time, command-line, process, user, device, event-type, and hash parameters.
- Applies native-column filters before normalization where possible; unavailable parent-process and hostname values are not fabricated.
- Always preserves Falcon correlation IDs and unmapped source fields in AdditionalFields.
