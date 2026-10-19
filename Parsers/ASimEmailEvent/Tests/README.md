# Microsoft Defender for Office 365 EmailEvents contribution

## Scope and status

New regular and filtering ASIM EmailEvent 1.0.0 parsers for the native Sentinel `EmailEvents` table. These parsers preserve individual recipient/update records. They do not read attachment/URL tables, deduplicate messages, expand arrays, or normalize post-delivery remediation events.

Local KQL syntax/binding and schema checks have run. Value assertions are prepared as a self-contained KQL query but have NOT been executed by a KQL engine. There has been no deployment, ingestion, private-email export, performance benchmark, or production validation.

Local results on October 15, 2026: eight focused .NET checks passed; the existing template validator passed 15 checks for each variant; six generated ARM JSON files parsed successfully. These results are static validation, not successful execution of the 14 mapping cases or 26 runtime control assertions.

## Mapping contract

| Source | Normalized output | Meaning or limit |
| --- | --- | --- |
| `TimeGenerated` | `EventStartTime`, `EventEndTime` | An instantaneous source record; no invented duration |
| Source table | `Type` | Retained as `EmailEvents` |
| Source purpose | `EventType=EmailDelivery` | Results describe delivery, not whether the security control succeeded |
| Product identity | `EventVendor`, `EventProduct`, `Dvc` | Reporting cloud service, not an invented appliance hostname or tenant identity |
| `ReportId` | `EventOriginalUid` | Not assumed globally unique |
| Workspace ID, message ID, recipient, timestamp, report ID | `EventUid` | SHA-256 of a serialized tuple; no source-record correlation |
| `SenderFromAddress`, `SenderFromDomain` | `EmailFromAddress`, `EmailFromDomain` | Visible header sender |
| `SenderMailFromAddress`, `SenderMailFromDomain` | `EmailMailFromAddress`, `EmailMailFromDomain` | Separate SMTP envelope sender |
| `RecipientEmailAddress` | `Dst` | The destination of this recipient-level event, not the complete To header |
| Native dynamic `To`, `Cc` | `EmailToRecipients`, `EmailCCRecipients` | Missing/null/non-array values become empty arrays; no fabricated header addresses |
| Valid `SenderIPv4`, otherwise valid `SenderIPv6` | `SrcIpAddr`, `IpAddr`, `Src` | Invalid IP values are not emitted as normalized IP addresses |
| `Subject`, `EmailLanguage`, `EmailSize` | `EmailSubject`, `EmailLanguage`, `EmailSizeBytes` | Size is converted to long; negative size becomes null |
| `AttachmentCount`, `UrlCount` | `EmailFileCount`, `EmailUrlCount` | Counts only; negative counts become null; detailed files/URLs are not invented |
| `Inbound`, `Outbound`, `Intra-org` | `Inbound`, `Outbound`, `Internal` | Unrecognized source direction becomes `Unknown` |
| Delivery location | `EmailDeliveryLocation` | Only Inbox/Folder, Junk, Quarantine and Deleted items map to allowed ASIM locations; originals retained |
| Delivery action/location | `EventResult`, `DvcAction` | See the table below |
| `ThreatTypes`, `ThreatNames` | `ThreatOriginalCategory`, `ThreatName` | Source strings retained without choosing the first member of a threat list |
| Threat verdict plus action | `EventResultDetails` | Malware/Phish retain detected verdicts; Spam implies `BlockedBySpamFilter` only when blocked; unspecified blocking is `Other` |
| `AuthenticationDetails` | SPF, DKIM and DMARC original/normalized results | Known values mapped independently; missing/malformed/unknown values do not become Pass |
| `EmailActionPolicy` | `RuleName`, `Rule` | Policy name retained without asserting it caused every failed delivery |
| `SenderObjectId` | `SrcUserId`, `SrcUserIdType` | ID type populated only when the source ID exists |
| `pack=true` | `AdditionalFields` | Complete original source-row snapshot, including unmapped/new source fields; no top-level schema drift |
| `pack=false` | `AdditionalFields={}` | Default, no source snapshot returned |

### Delivery semantics

| Source condition | EventResult | DvcAction |
| --- | --- | --- |
| Delivered | Success | Delivered |
| Junked | Success | Delivered, with Junk location if reported |
| Replaced | Success | Modified |
| Blocked and Quarantine | Failure | Quarantined |
| Other Blocked | Failure | Blocked |
| Failed/Dropped location | Failure | Source action still normalized independently |
| Unknown action without an explicit failed/dropped location | NA | NA |

An email can contain a detected threat and still have a successful delivery result. Delivery success does not mean the message is safe. Unknown values and original action/location/authentication values are retained rather than forced into unsupported enumerations.

Missing mandatory timestamp or recipient is not repaired with an invented value. The parser retains the record and emits an explicit `EventMessage` diagnostic. Those rows still fail mandatory-data conformance and are intentional malformed-source cases, not valid production examples.

Source fields unavailable in this table are left unmapped. In particular, we do not invent reply-to, protocol, reporter/source hostnames, destination IP, attachment details, URL lists, or a source event severity. Missing recommended fields are reviewable limitations, not permission to guess.

## Filters

The filtering variant supports every current EmailEvent unifier parameter, plus `disabled`.

- Time bounds are inclusive and applied to native `TimeGenerated`.
- Sender and subject use the standard KQL `has_any` term semantics, not arbitrary substring matching.
- Recipient searches consider the actual recipient and valid To/Cc arrays.
- IP prefixes apply to the selected normalized source IP. IPv4 is preferred when both IP fields are valid. Prefixes are escaped as literals before constructing a scalar regex, which supports IPv6 without `mv-*` expansion. This is the deliberate exception to preferring native IPv4-only prefix helpers.
- Direction, delivery-location and result filters use normalized values. Case-insensitive matching is supported for these enum values.
- Cheap native predicates run before normalization. Normalized predicates run before JSON authentication parsing and the remaining mappings.
- Global and source-specific exclusions are wired into both local unifiers.

## Fixtures and evaluation

`EmailEventsSynthetic.json` contains 14 synthetic cases with independently specified expected fields. All records were authored for this contribution. They are NOT production telemetry or a redistribution of external sample content.

Cases cover delivery, quarantine/phishing, junk/spam, replacement/malware, outbound/external routing, failed delivery, unknown values, IPv6 fallback, both IP versions, missing optional fields, malformed dynamic/JSON values, negative counts/sizes, invalid IPs, and missing required fields.

The ten-row CSV under `Sample Data\ASIM` contains the first ten synthetic cases and all 55 columns in the captured native source contract. The malformed mandatory-field cases are deliberately separate.

The older public Elastic streaming fixture informed source-shape research only. Its event envelope is not a native Sentinel row and it does not establish current production correctness.

`EmailEventsRegression.kql` embeds source hashes to prevent silently testing stale parser copies. Hashes use UTF-8 text with LF-normalized line endings so Windows and Linux checkouts agree; the regression checks cover both LF and CRLF source text. The query contains the real parser variants and unifiers, a synthetic-only source table and an empty test watchlist. It reads no external table and performs no write. The Python generation and template-check helpers used during development are retained locally and are not included in this contribution.

The regression query checks both variants against 14 mapping cases and includes 26 assertions for cardinality, disabling, time bounds, positive/negative filters, IPv4/IPv6 prefixes, packing, malformed-source diagnostics and the normalized query workflow. Zero result rows means success only when the query has actually been executed.

## Reproduce local checks

Run the focused static checks from the repository root:

```powershell
dotnet test .script\tests\KqlvalidationsTests\Kqlvalidations.Tests.csproj --filter FullyQualifiedName~ASimEmailEventsTests
```

The focused .NET tests use the repository's existing Kusto.Language dependency. They bind both variants to the current 55-column source contract, repeat binding without optional To/Cc/EmailSize columns, verify normalized field names/types/mandatory columns against `ASimTester.csv`, check identical variant schemas and event-local structure, and bind the synthetic regression workflow without external tables.

These checks are static analysis, NOT a substitute for KQL engine execution or ASimDataTester value validation.

Generate local ARM files using the existing converter without deleting the ARM directory:

```powershell
python ASIM\dev\ASimYaml2ARM\KqlFuncYaml2Arm.py -m asim -d Parsers\ASimEmailEvent\ARM Parsers\ASimEmailEvent\Parsers
```

This only generates files. It does not deploy them.
The combined template references the upstream `master` branch. Its new nested targets will not be available there until publication; retain these files for review, not as evidence of a successful deployment.

## Intended normalized query

The following query is represented in the compiled inline regression workflow:

```kusto
imEmailEvent(
    eventresult="Failure",
    emaildirection_in=dynamic(["Inbound"])
)
| project TimeGenerated, EmailFromAddress, Dst, EmailSubject, DvcAction, EventResultDetails
```

`imEmailEvent` refers to this contribution's local/custom unifier. This draft does not change the service's installed `_Im_EmailEvent` built-in parser. Do not claim built-in availability before maintainer integration or approved custom registration.

## Review and release gates

1. Confirm mappings with the EmailEvent schema and source maintainers.
2. Review cloud-service `Dvc` identity, delivery-result semantics, source field/version compatibility and the IP-prefix implementation.
3. Obtain approved current representative data and a permitted execution environment. Validation completed so far is local static analysis only.
4. Execute the prepared KQL assertions, schema tester and data tester, then check the intended normalized query on current source rows.
5. Link the four updated/new changelog entries to the associated pull request.
6. Complete maintainer review and runtime validation before merging. Deployment and sample ingestion are separate operations, not part of opening this contribution.

## Reusable validation assets and AI assistance

Included reusable assets are the source schema snapshot, mapping contract, labeled fixtures, focused Kusto binding tests and self-contained KQL regression query. The Python development helpers are retained locally, outside this contribution.

AI assisted source comparison, mapping development, fixture generation, implementation and local validation. Static checks identified a regression-harness join-key mistake, which was corrected. Inspection also tightened packing, filtering order and result-detail semantics. This contribution does not claim production correctness, performance improvements or measured development-time savings.

## Source references

- [EmailEvent normalization schema](https://learn.microsoft.com/en-us/azure/sentinel/normalization-schema-email)
- [Native Sentinel EmailEvents schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/emailevents)
- [Defender source behavior and streaming-update note](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailevents-table)
- [ASIM authoring guidance](https://learn.microsoft.com/en-us/azure/sentinel/normalization-develop-parsers)
- [Public streaming test fixture inspected during research](https://github.com/elastic/integrations/blob/f4e54aeb9e48cdbf30f94f1fe6b7b5f2ed8395f7/packages/m365_defender/data_stream/event/_dev/test/pipeline/test-email.log)
