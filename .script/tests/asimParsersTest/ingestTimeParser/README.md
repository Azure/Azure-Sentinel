# ASIM ingestion-time parser validation

This folder contains the trusted implementation used by the ingestion-time
parser validation workflows.

## Entry points

The five `asim_*.py` files at the folder root are stable command-line entry
points. They contain argument parsing and re-export the public interfaces used
by tests. Business logic lives under `asim_ingestion/`.

| Entry point | Responsibility |
|---|---|
| `asim_ingest_time_validation.py` | Discover affected ITP targets and run static parser validation |
| `asim_fixture_preparation.py` | Prepare one immutable, typed, timestamp-rebased fixture |
| `asim_ingestion_harness.py` | Execute raw and parser DCR ingestion |
| `asim_ingestion_validation.py` | Validate filtering, ASIM data, and optional QTP parity |
| `asim_ingestion_workflow.py` | Build workflow matrices, reports, annotations, and cleanup requests |

## Implementation packages

```text
asim_ingestion/
├── parser/
│   ├── common.py             Safe YAML loading, shared models, repository evidence
│   ├── kql.py                DCR policy and AST-derived fixture/source checks
│   ├── kusto_analyzer.py     Bridge to the trusted Microsoft Kusto.Language helper
│   ├── discovery.py          ITP trigger fan-in and optional QTP resolution
│   └── static_validation.py  Field-level ITP and optional QTP eligibility validation
├── fixtures/
│   ├── timestamps.py         Exact Kusto ticks and run/target namespaces
│   └── data.py               CSV loading, schema resolution, conversion, artifacts
├── azure/
│   ├── common.py             Azure configuration, result models, query/artifact helpers
│   ├── client.py             ARM, Log Analytics, and Logs Ingestion operations
│   └── runner.py             Raw snapshot and parser-DCR orchestration
├── runtime/
│   ├── queries.py            Filter, ASIM tester, and QTP query construction
│   ├── parity.py             Typed canonical multiset comparison
│   └── validator.py          Runtime filtering, ASIM data, and parity orchestration
└── workflow/
    ├── contracts.py          Matrix validation, target export, and deterministic cleanup
    └── reporting.py          Result aggregation, summaries, and annotations
kusto_analyzer/
├── Program.cs                Syntax and AST fact extraction without query execution
└── kusto_analyzer.csproj     Locked .NET 8 Microsoft.Azure.Kusto.Language helper
```

## Validation flow

```text
discover target
  → static parser validation
  → prepare immutable fixture
  → freeze a typed parser-input snapshot from the fixture
  → evaluate ParserFilterQuery against an inline fixture datatable
  → upload fixture rows directly through the parser DCR
  → verify exact per-timestamp target visibility
  → run ASIM data checks
  → optionally replay the fixture to SourceRawTable using InputStream
  → execute the mapped QTP and compare parity when replay succeeds
  → clean up DCRs and publish the report
```

Fixture preparation matches row column names to repository schema names
case-insensitively and rewrites them to the schema's canonical casing before
type conversion. Two fixture columns that collapse to the same name are
rejected. Snapshot construction repeats the case-insensitive uniqueness check
so it cannot submit an invalid DCR stream declaration.

The legacy `VerifyASimParserTemplate.py` validator is limited to query-time
parser files under `Parsers/`; its changed-file filter excludes
`IngestTimeParsers/`. Ingestion-time parsers are validated by the dedicated
workflow above, without requiring query-time union-parser metadata or a
corresponding `vim*` parser.

Static KQL parsing uses the official `Microsoft.Azure.Kusto.Language` package,
pinned to version `12.4.1`, through a trusted .NET 8 helper. The helper parses
but never executes parser KQL and returns syntax diagnostics plus AST facts to
Python, including normalized statements and operators, named assignments, and
tabular source references. `KQL001` reports official syntax diagnostics, while
`KQL000` reports a helper build, execution, or contract failure. Python retains
the DCR-specific policy decisions, but filter consistency, fixture metadata,
QTP source matching, and runtime pass-through detection all consume helper
facts instead of custom KQL tokenization. CI restores the NuGet dependency in
locked mode for discovery, template validation, and ingestion validation and
passes the built trusted DLL through `ASIM_KUSTO_ANALYZER_DLL`.

`ParserFilterQuery` and `ParserQuery` must each contain exactly one expression
statement whose pipeline root is the lowercase name `source`. Leading `let`
statements, multiple statements, parenthesized roots, external-table roots,
and differently cased source names are rejected before operator-policy checks.

`ParserQuery` is submitted to the parser DCR exactly as decoded from YAML.
Static validation rejects queries longer than 14,800 characters with
`KQL044`; comments, indentation, and line breaks count toward that limit.
The workflow does not compact or otherwise rewrite the parser query.

Parser validation does not depend on raw-table replay. QTP source replay is
optional. If its table or DCR cannot be established, the report records a
warning and blocks QTP/parity without failing the required parser validation
stages. Once the raw DCR exists, upload or visibility failures fail the target;
QTP execution and parity also fail the target when they run and fail.
Parser ingestion is reported as passed only when both upload and target
visibility pass.

Before creating the optional raw-replay DCR, the harness reads destination
column types from the workspace Tables management API, including both
`columns` and `standardColumns`. Unlike Log Analytics query-result metadata,
this preserves GUID types required for ingestion. It casts fixture columns
whose input types differ from the destination, including string IDs to `guid`
with `toguid`. DCR input declarations and the immutable fixture remain
unchanged; matching columns keep the pass-through transform.
Unavailable or invalid destination metadata follows the existing replay
setup warning path and blocks QTP/parity. The parser DCR is unaffected.
Fixture GUID values must be valid GUID strings: `toguid` converts malformed
values to null, so type alignment alone cannot repair invalid sample IDs.

Before ASIM data testing, the `ASimDnsActivityLogs` table slice normalizes
`ThreatFirstReportedTime` and `ThreatLastReportedTime` to `datetime` and
`ThreatOriginalRiskLevel` to `string`. This accommodates the documented
physical-table/logical-ASIM type discrepancy, preferring the corrected `_d`
and `_s` columns and falling back to casts of the legacy columns. This
normalization affects only the data-tester input, not ingestion or QTP parity.

For `ASimAlertEventLogs`, the data-tester input casts `FileSize` to `long`.
The [physical table](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/asimalerteventlogs)
stores this column as `string`, while logical ASIM requires `long`. This
normalization likewise leaves ingestion and QTP parity unchanged.

Static validation requires `ParserFilterQuery` to contain a `where` stage when
`ParserQuery` contains one. This is a presence check only; it does not require
all parser `where` stages to be copied into the filter query.

`Standard` parsers must declare a non-`none` `InputStream`. `Workspace`
parsers may omit `InputStream` or declare it. Any declared non-`none` stream
must use the supported stream-name format.

`qtpSourceReplay` persists the latest `observedSchema`, `observedRows`, and
`observedCountsByTimestamp` from raw-table visibility checks. These remain
available in `validation-result.json` when visibility detects unexpected,
duplicate, or incomplete rows.

Exact-row visibility timeouts include `expectedCounts`, the last successful
`observedCounts`, `missingTimestamps` (timestamps with fewer rows than expected),
and `observedQueryTable` in the error details, including when the shared deadline
expires between polls or during settling. Before any successful observation,
the observed counts are empty and the query table is null. Shared-deadline
errors retain their original stage and message; query failures remain unchanged.
The validation artifact records `targetVisibility` as `passed`, `failed`, or
`not-run`; failed outcomes retain their original error stage and diagnostic
details. The report nests this explicit result under the existing
`parserIngestion` stage, whose public key remains unchanged. Older artifacts
without `targetVisibility` use the exact legacy `target-visibility` error stage
or a generic deadline error together with target-visibility timing and no
output-validation timing to identify this failure; other generic query errors
are not attributed to visibility.

The report's `schema` stage reflects the actual
`outputValidation.schemaValidation` result and is `not-run` when that evidence
is absent, even if a parser DCR exists. That field is emitted only after
ASimDataTester succeeds and its authority is `parser-dcr-output-stream`; it
does not represent a separate ASimSchemaTester execution. These diagnostics do
not resolve the underlying canary ingestion timeout.

QTP parity stores the complete `qtp_schema`, `qtp_rows`, `itp_schema`, and
`itp_rows` under `outputValidation`. It derives `intersect_schema` from shared
column names, excluding the platform-managed `Type` column, and records both
QTP and ITP types. A shared-column type mismatch fails schema parity. When
shared types are consistent, it filters both row sets into
`qtp_rows_filtered` and `itp_rows_filtered` and runs the typed duplicate-aware
row comparison across that shared schema.

For the dynamic `AdditionalFields` property bag only, parity compares the
case-sensitive set of top-level key names per row, not their values. It ignores
the exact platform-managed keys `TenantId`, `TimeGenerated`, `Type`, and
`_ResourceId` when they occur inside `AdditionalFields`; differently cased
keys remain strict. Nested keys and values are not compared. This accommodates
ingestion serialization changes such as date-shaped strings becoming
datetimes and platform metadata unavailable to DCR transformations. Row
counts, duplicate multiplicity, schema types, and values in every other column
remain strict. An empty property bag is still distinct from null or a
non-object value; non-object `AdditionalFields` values retain the existing
value comparison. Canonical mismatch examples replace retained property-bag
values with null to represent key presence. The stored QTP/ITP rows and
filtered rows retain their original values.

## Tests

Run the complete regression suite from the repository root:

```powershell
python -m unittest discover `
  -s ".script\tests\asimParsersTest\ingestTimeParser\tests" `
  -p "test_asim_*.py"
```
