# Advanced Security Information Model (ASIM) Email Event parsers

This template deploys all ASIM Email Event parsers.

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Email Event normalization schema reference](https://aka.ms/ASimEmailEventDoc)

## Microsoft Defender for Office 365

`ASimEmailEventMicrosoftDefenderOffice365` and
`vimEmailEventMicrosoftDefenderOffice365` normalize the native Sentinel
`EmailEvents` table to EmailEvent 1.0.0. They preserve individual recipient/update
records and distinguish delivery outcomes from threat detection.

Both support `disabled` and optional packing. The filtering variant supports the
standard EmailEvent parameters. Supplied records are synthetic; production-data
validation remains pending.

Uncorrected tester metadata may reject valid recipient string arrays. The shared
ingestion script also skips native `EmailEvents`, and the table reference lists
Ingestion API support as No. A maintainer-supported hosted validation route is
still required. See [PR #15373](https://github.com/Azure/Azure-Sentinel/pull/15373)
for the executed checks, disclosed adaptations and remaining limitations.