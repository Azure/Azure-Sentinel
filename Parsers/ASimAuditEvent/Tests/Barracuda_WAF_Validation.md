# Barracuda WAF local validation - 2026-10-10

These CSVs are results from Microsoft's ASimSchemaTester and ASimDataTester
queries executed in a local Kusto emulator. They are **not Sentinel workspace
captures**, canary ingestion results, or tests against a live Barracuda appliance.
Workspace validation remains pending.

## Inputs and execution

- Source: the updated `Sample Data/ASIM/Barracuda_WAF_AuditEvent_IngestedLogs.csv`.
- Tester definitions and ASimTester.csv: Azure-Sentinel base commit
  `55296e614ce092a97a54096b97672800ae9fd197`.
- Engine: `2026.09.10.1417-2636-815860b-master`.
- The test harness replaces tester `externaldata` reads with literal tables of
  the same CSV values, preserving the tester logic. IANA dependency tables are
  cached, not repeatedly downloaded.
- WAF CSV results use the custom-table sample. CEF checks use controlled
  CommonSecurityLog-shaped records derived from the public sample, including
  lower-case process names. These are projections, not ingestion captures.
  The failed-login control uses `ProcessName=unsuccessful_login` to resolve the
  legacy sample's disagreement between its structured name and embedded CEF.
- Both parameterless and filtering parser variants were exercised. Across all
  six modified source parsers and their input branches, 16 schema/data runs
  returned zero error-level findings and no extra unnormalized columns.
- Entity-key empty values are intentional placeholders required by the current
  parser guidance. Data-test Info findings are retained in the CSVs.

## Remaining warnings

Recommended fields without an established source mapping remain warnings;
values were not invented to suppress them. See each SchemaTest CSV for the
exact list. Device/source addresses were not copied to target/destination
fields without evidence that they identify the target. Empty result details
are retained when the input supplies no reason.

## Other local checks

66 native behavior queries passed for routing, timeout normalization, preserved
control mappings, disabled behavior and filtering. Seven additional queries
executed the actual Barracuda call expressions extracted from imAuditEvent,
checking positive, negative and combined actor/object filter forwarding.
This is a focused check of those calls, not a workspace execution of every
source in the full unifier. Six source-parser template checks pass, and the
seven generated ARM query bodies match their YAML.

The repository .NET 8 KQL test ran with this filter:

```text
FullyQualifiedName~Validate_ParsersFunctions_HaveValidKql&(DisplayName~Barracuda|DisplayName~imAuditEvent.yaml)
```

All 16 selected tests passed, including unchanged Barracuda controls and the
AuditEvent unifiers. The workflow's union template exclusion is preserved;
unrelated source parsers were not migrated.

## Cached tester dependencies

- `ASimTester.csv`: SHA-256 `792dffd4352668bd5e22e3a1a7210ca04375709455d1bb4e6b54cccc37e1a7ee`
- `protocol-numbers-1.csv`: SHA-256 `e704ee14e69347681b3a6271af02195a9741236074fc311449ebb032101bdf2c`
- `dns-parameters-4.csv`: SHA-256 `215ee79b6aabcf4d4b2a911f0513cd27da4fc7820c274afa81240b8589f340cc`
- `dns-parameters-6.csv`: SHA-256 `068551e152ea39e758e7ef29e3d88cb33e63cda7a4bd7f3ad718dbf268370e57`
