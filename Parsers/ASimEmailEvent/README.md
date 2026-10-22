# Advanced Security Information Model (ASIM) Email Event parsers

This template deploys all ASIM Email Event parsers.

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Email Event normalization schema reference](https://aka.ms/ASimEmailEventDoc)

## Proofpoint POD MailLog

`ASimEmailEventProofpointPODMailLog` and `vimEmailEventProofpointPODMailLog`
normalize the CCP table `ProofpointPODMailLog_CL` to EmailEvent 1.0.0.
The legacy `ProofpointPOD_maillog_CL` table and `ProofpointPODMessage_CL` are
not inputs to these functions. Both parsers read the source once and emit at
most one row for each source row. They select message-related sendmail records
with a queue ID and either an envelope sender property or nonempty envelope
recipients; TLS-only and other non-message records are not normalized.

### Evidence and mappings

The source contract is the solution's
[CCP table definition](../../Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofPointEmailSecurity_CCP/ProofpointPOD_Table_MailLog.json)
and [DCR transform](../../Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofPointEmailSecurity_CCP/ProofpointPOD_DCR.json).
The [20 existing raw samples](../../Sample%20Data/Custom/ProofpointPOD_maillog_CL.json)
provide the observed `sm` and device fields. The ASIM fixture
`Sample Data/ASIM/Proofpoint_POD MailLog_EmailEvent_IngestedLogs.csv` is a
local transformation of those samples into the CCP shape, not a workspace export.
Its timestamps use the source `ts` value for reproducibility; the real DCR
sets `TimeGenerated` to ingestion time and `eventTime` to `todatetime(ts)`.

| Source | ASIM output |
| --- | --- |
| `TimeGenerated` | `TimeGenerated` |
| `eventTime` (fallback: `TimeGenerated`) | `EventStartTime`, `EventEndTime` |
| `id` | `EventOriginalUid`; namespaced as `EventUid` |
| `data` | `EventMessage` |
| `pps.agent` (fallback: `metadata.origin.data.agent`) | `Dvc` and device hostname/domain fields |
| Presence of `sm.from` or nonempty `sm.to`, with `sm.qid` | Select receipt/delivery records; nonempty `sm.to` identifies `EmailSent`, otherwise `EmailReceived` |
| `sm.relay` | Remote host/IP; source on receipt, destination on delivery |
| Reporting device | Destination on receipt, source on delivery |
| `sm.from` | `EmailMailFromAddress`, `EmailMailFromDomain` after removing surrounding whitespace/angle brackets |
| `sm.sizeBytes` | `EmailSizeBytes` as a long |
| `sm.proto`, `sm.mailer` | `EmailProtocolName` (`SMTP` for SMTP/esmtp) |
| `sm.dsn` | `EventResult`: `2.x.x` success, `4.x.x`/`5.x.x` failure, otherwise `NA` |
| `sm.dsn`, `sm.stat` | `EventOriginalResultDetails` |
| `sm.stat` starting with `Sent`, with successful DSN | `DvcAction=Delivered` for transport handoff, not proof of inbox placement |
| `sm`, `tls`, `pps`, `metadata` | Original objects in `AdditionalFields` when `pack=true`; empty dictionary otherwise |

The reporting device may be either endpoint of an SMTP hop; `EmailDirection`
is therefore `Unknown`, not an inferred organizational inbound/outbound direction.
Receipt rows do not contain a delivery result and return `EventResult=NA`.
The parser does not repair the truncated sender present in one repository sample:
sender strings without `@` are left unmapped, with the original in
`AdditionalFields.sm` when packing is enabled. This is not full RFC mailbox validation.

`sm.from` and `sm.to` are **envelope** addresses, not `From`/`To` header fields.
The parser deliberately leaves header sender/recipient, subject, Reply-To,
delivery location, attachment counts and SPF/DKIM/DMARC results unmapped.
Envelope recipients and queue/message identifiers remain available in
`AdditionalFields.sm`; the parser does not choose one recipient, expand arrays
or correlate receipt and delivery rows. TLS verification is not an email
authentication result.

### Filtering and validation status

The filtering parser supports event-time bounds (with ingestion-time fallback
only when `eventTime` is null), source/destination IPv4 prefixes, normalized
result and the known direction `Unknown`. Both endpoints are checked for the
IPv4-prefix filter; IPv6 prefix matching is not implemented.
Nonempty `emailfromaddress_has_any`, `emailrecipient_has_any`,
`emailsubject_has_any` or `emaildeliverylocation_in` filters return no rows:
the corresponding normalized header/location fields are unavailable, even
when envelope addresses are present. All parameters are forwarded by
`imEmailEvent`. `disabled=true` returns no rows.

Live sampling, KQL execution, `ASimSchemaTester`, `ASimDataTester` and filter
tests are **deferred by user request**, not passed. The supplied workspace
did not contain this table. No table creation, ingestion or deployment has
been performed. The Proofpoint API reference requires sign-in; task-specific
Azure DevOps acceptance criteria were also unavailable. SMTP status meanings
follow [RFC 3463](https://www.rfc-editor.org/rfc/rfc3463).
Before release, verify the source shape and mixed receipt/delivery mappings
against real CCP records, run both ASIM testers and filter tests, and add the
actual pull-request links to the four affected changelogs. Missing recommended
header/security fields are intentional source limitations, not evidence of
empty headers or zero attachments.

The repository's focused `Validate_ParsersFunctions_HaveValidKql` tests currently
fail with `KS204`: their custom-table catalog does not define
`ProofpointPODMailLog_CL`. The standalone offline compiler checks use the
connector's declared schema and pass, but do not replace those repository tests.
A maintainer must add the CCP table definition to the protected validation
catalog before those tests can pass; this parser task does not modify tooling
or test implementation.