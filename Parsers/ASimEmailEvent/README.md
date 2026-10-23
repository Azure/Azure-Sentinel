# Advanced Security Information Model (ASIM) Email Event parsers

This template deploys all ASIM Email Event parsers.

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Email Event normalization schema reference](https://aka.ms/ASimEmailEventDoc)

## Proofpoint POD message parser

`ASimEmailEventProofpointPODMessage` normalizes the CCP connector's
`ProofpointPODMessage_CL` table to EmailEvent 1.0.0. It does not read the legacy
`ProofpointPOD_message_CL` table or the separate mail-log table.

The source contract is the solution's `ProofpointPOD_Table_Message.json` and
`ProofpointPOD_DCR.json`. Nested field mappings are supported by the repository's
`Sample Data/Custom/ProofpointPOD_message_CL.json` message payload. The DCR
converts its `ts` to the native datetime `eventTime`; `TimeGenerated` is ingestion
time, not the message event time.

| Source | Normalized fields |
| --- | --- |
| `eventTime` | `EventStartTime`, `EventEndTime` |
| `guid` | `EventOriginalUid` |
| `pps.agent`, `metadata.origin.data.agent` | `Dvc`, `DvcFQDN`, `DvcHostname`, `DvcDomain`, `DvcDomainType` |
| `pps.version`, `metadata.origin.data.version` | `EventProductVersion` |
| `connection.ip`, `connection.host`, `connection.country` | `Src`, `SrcIpAddr`, `IpAddr`, `SrcFQDN`, `SrcHostname`, `SrcDomain`, `SrcDomainType`, `SrcGeoCountry` |
| `connection.protocol` | `EmailProtocolName` (`smtp:smtp` becomes `SMTP`) |
| `envelope.from` | `EmailMailFromAddress`, `EmailMailFromDomain` |
| `envelope.rcpts` | `Dst` (one address, or the JSON recipient array for a multi-recipient message) |
| `msg.parsedAddresses.from` | `EmailFromAddress`, `EmailFromDomain` when exactly one address is present |
| `msg.parsedAddresses.to` | `EmailToRecipients` |
| `msg.normalizedHeader.subject` | `EmailSubject` when exactly one subject is present |
| `msg.sizeBytes`, `msg.lang` | `EmailSizeBytes`, `EmailLanguage` |
| `filter.routeDirection` | `EmailDirection` |
| `filter.disposition` | `DvcOriginalAction`, `DvcAction` (`reject`/`discard` become `Blocked`; other dispositions remain `NA`) |
| `filter.modules.spf.result` | `EmailSpfOriginalResult`, `EmailSpfResult` |
| `filter.modules.dmarc.filterdResult` | `EmailDmarcOriginalResult`, `EmailDmarcResult` |
| `filter.modules.dkimv` | `EmailDkimOriginalResult`, `EmailDkimResult`, `EmailDkimDomain` only when exactly one signature result is present |
| Source dynamic objects, including `msgParts` | `AdditionalFields` only with `pack=true` |

These are inspection events, not delivery confirmations: `EventType` is
`EmailInspection`, `EventResult` is `NA`, and `EventCount` is 1. A filter
`continue` action does not establish delivery to an inbox. No severity or
threat classification is inferred from undocumented numeric scores.

The parser neither expands recipients/MIME parts nor chooses an arbitrary
sender or DKIM signature from multiple values. Attachment and URL counts are
not inferred from MIME-part counts, which include inline body parts.
Unmapped fields, multi-valued sender/subject/signature details, and source
actions remain available with `pack=true`.

### Filtering

`vimEmailEventProofpointPODMessage` exposes the standard EmailEvent parameters
and is registered in `imEmailEvent`. The parameterless parser is registered
in `ASimEmailEvent`. Both accept `pack`; source parsers also accept `disabled`.
The usual `ASimDisabledParsers` watchlist can disable either source parser
using `ExcludeASimEmailEventProofpointPODMessage` or
`ExcludevimEmailEventProofpointPODMessage`, respectively.

Time limits apply inclusively to native `eventTime`, not ingestion time.
Sender, To-recipient, and subject filters use KQL case-insensitive `has_any`
term matching; they do not implement arbitrary substring matching. Direction
matching is case-insensitive. IP filtering uses `has_any_ipv4_prefix` and
supports IPv4 prefixes only; IPv6 addresses remain available in unfiltered output.
Recipient filtering covers the normalized To-header array, not envelope-only
recipients or unverified Cc/Bcc fields.

The parser applies `parse_json(tostring(...))` to the connector's dynamic
objects before reading nested fields. This supports both normal dynamic
objects and JSON strings produced when the repository's CSV-based ASIM
sample-data ingester transports dynamic fixture columns.

Only `eventresult='*'` or `'NA'` can match these inspection events. A nonempty
`emaildeliverylocation_in` returns no rows because delivery location is not
available. Empty arrays and null time bounds leave the corresponding filter
unrestricted. Multiple nonempty parameters are combined with AND.

### Deferred validation and publication

The user explicitly deferred live validation and authorized completing both
source parsers and unifier registration offline. ARM artifacts are generated
and committed by the repository's GitHub action; no manual ARM edits are part
of this change.
The supplied workspace did not contain `ProofpointPODMessage_CL`; live sampling,
Log Analytics KQL execution, `ASimSchemaTester`, `ASimDataTester`, and
live filter-behavior tests have not passed and remain deferred. Synthetic
fixtures are regression inputs, not observed workspace telemetry. The current
ASIM filter-validation script does not support EmailEvent, so its CI filter
job fails before testing parser behavior; its implementation was not changed.
The Azure DevOps task details and vendor API documentation require sign-in;
task-specific acceptance criteria and source enumerations remain unverified.
The implementation is tracked in [PR #15409](https://github.com/Azure/Azure-Sentinel/pull/15409).

The `Tests/ProofpointPODMessage.Tests.ps1` checks the source contract, metadata,
field projection, forbidden operators, fixture coverage, parameter bindings,
unifier registrations and inferred KQL
output types offline using the repository's Kusto.Language dependency:

```powershell
dotnet build .script\tests\KqlvalidationsTests\Kqlvalidations.Tests.csproj
.\Parsers\ASimEmailEvent\Tests\ProofpointPODMessage.Tests.ps1
```

These checks do not execute records and are not a substitute for the live ASIM
schema/data/filter testers. The source-schema CSV and KQL validation catalog
fixture mirror the connector's table definition; creating fixtures does not
ingest data.
