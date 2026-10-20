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
`EmailEvents` table to EmailEvent 1.0.0. The filtering variant supports the
standard EmailEvent parameters. Both support `disabled` and opt-in `pack`.

Each source recipient/update record is preserved independently. Delivery success
is distinct from threat detection. The parsers do not join other event tables,
expand arrays, deduplicate messages, or normalize post-delivery remediation
events. Missing source values are not invented. Packing retains unmapped source
fields; the default is an empty `AdditionalFields` bag.

### Validation status and limitations

Development followed the official ASIM parser skill files directly, with
disclosed read-only adaptations rather than an unmodified registered-skill
invocation. Inline synthetic-fixture execution covered 21 mapping cases per
variant, 78 expected-field assertions per variant, and 31 additional runtime
controls. These are executed development checks, not production-data validation.

Official schema validation reported no errors and 11 unavailable recommended-field
warnings per variant. Unchanged data-tester metadata rejects valid recipient
string arrays because `ArrayValuesType` is blank. A separate query-only correction
of the three recipient-array metadata entries produced no data errors on 17
conformance records; numeric and mixed-array negative controls remained rejected.
Uncorrected deployed metadata may still report those errors.

The upstream filter harness has no EmailEvent map and assumes a single filtered
column. A local adapter using exact event identities and multiplicities for
Dst/To/Cc recipient matching passed 60 checks on full-header fixtures. This is an
adapted result, not an unchanged official-suite pass. No metadata corrections,
harness adapters or development scripts are included in this contribution.

### Shared ingestion limitation

Every supplied CSV row routes to `Type=EmailEvents`; the KQL catalog location
under `CustomTables` does not make it a custom log table. The current shared ASIM
ingestion script does not allowlist `EmailEvents` as a supported built-in and
skips it as unsupported. The native table reference also lists Ingestion API
support as No. A maintainer-supported hosted validation route is still needed.
The CSV contains JSON-encoded dynamic values; successful CSV parsing is not proof
of ingestion or of preservation of native dynamic types.

Synthetic samples do not establish representative source correctness. Real-data
validation, performance evaluation, acceptance of source-field warnings, and
review of authentication serialization remain pending.