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
│   ├── kql.py                KQL tokenization and deterministic compatibility checks
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
```

## Validation flow

```text
discover target
  → static parser validation
  → prepare immutable fixture
  → freeze a typed parser-input snapshot from the fixture
  → evaluate ParserFilterQuery against an inline fixture datatable
  → upload fixture rows directly through the parser DCR
  → run ASIM data checks
  → optionally replay the fixture to SourceRawTable using InputStream
  → execute the mapped QTP and compare parity when replay succeeds
  → clean up DCRs and publish the report
```

Parser validation does not depend on raw-table replay. QTP source replay is
optional. If its table or DCR cannot be established, the report records a
warning and blocks QTP/parity without failing the required parser validation
stages. Once the raw DCR exists, upload or visibility failures fail the target;
QTP execution and parity also fail the target when they run and fail.

Before ASIM data testing, the `ASimDnsActivityLogs` table slice normalizes
`ThreatFirstReportedTime` and `ThreatLastReportedTime` to `datetime` and
`ThreatOriginalRiskLevel` to `string`. This accommodates the documented
physical-table/logical-ASIM type discrepancy, preferring the corrected `_d`
and `_s` columns and falling back to casts of the legacy columns. This
normalization affects only the data-tester input, not ingestion or QTP parity.

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

QTP parity stores the complete `qtp_schema`, `qtp_rows`, `itp_schema`, and
`itp_rows` under `outputValidation`. It derives `intersect_schema` from shared
column names, excluding the platform-managed `Type` column, and records both
QTP and ITP types. A shared-column type mismatch fails schema parity. When
shared types are consistent, it filters both row sets into
`qtp_rows_filtered` and `itp_rows_filtered` and runs the typed duplicate-aware
row comparison across that shared schema.

## Tests

Run the complete regression suite from the repository root:

```powershell
python -m unittest discover `
  -s ".script\tests\asimParsersTest\ingestTimeParser\tests" `
  -p "test_asim_*.py"
```
