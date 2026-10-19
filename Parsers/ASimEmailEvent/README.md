# Advanced Security Information Model (ASIM) Email Event parsers

This template deploys all ASIM Email Event parsers.

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Email Event normalization schema reference](https://aka.ms/ASimEmailEventDoc)

## Source-specific parsers

Microsoft Defender for Office 365 `EmailEvents` is supported by the regular
`ASimEmailEventMicrosoftDefenderOffice365` and filtering
`vimEmailEventMicrosoftDefenderOffice365` parsers.

See [mapping notes, synthetic fixtures and validation limits](Tests/README.md).
The fixtures are synthetic; local syntax/schema checks do not establish production correctness.