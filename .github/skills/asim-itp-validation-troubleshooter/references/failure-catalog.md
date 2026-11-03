# ASIM ingestion-time validation failure catalog

Use this catalog after collecting the exact run artifacts. The earliest failed
required stage is normally the causal failure.

## Stage map

| Stage | Primary evidence | Common causes | Recommended checks |
|---|---|---|---|
| Security gate | Security-gate job log | Fork lacks `SafeToRun`; approver lacks write access; new commit removed approval | Verify event action, label, sender permission, and whether the PR synchronized after approval |
| Checkout | Job step timestamps and checkout log | Full all-branch/tag fetch; transient GitHub transfer; job timeout | Identify the exact fetch refspec and duration; distinguish checkout from discovery |
| Discovery | `discovery.json`, `matrix.json` | Wrong path/casing; no canonical ITP change; target limit; malformed parser index | Compare `changedPaths`, `changedParserPaths`, `indexErrors`, and `targets` |
| Counterpart | `target.json`, `report.json` | Missing/ambiguous QTP; mismatched product/schema/source table | Review `pairStatus`, candidates, and evidence tier |
| Template | `static-validation.json` | Invalid YAML/metadata; unsupported KQL; query too long; invalid source-rooted shape | Report every finding code, field, and message |
| Fixture | `prepared-fixture.json`, discovery errors | Missing exact fixture; invalid CSV; wrong `Type`; unsupported values/types | Use the exact resolved fixture path and source table |
| Filtering | `validation-result.json` | Filter drops/duplicates rows; timestamp mismatch; prerequisite parse missing | Compare raw/selected counts by canonical timestamp |
| Parser DCR | `validation-result.json.error` and ingestion job log | Azure KQL compile error; undefined symbol; invalid stream/table; transform too long | Preserve nested Azure code, message, target, line, and column |
| Parser ingestion | Upload and visibility evidence | Schema/type mismatch; Logs Ingestion rejection; missing/duplicate rows; visibility timeout | Compare attempted rows, accepted batches, observed rows, and counts |
| Schema | `report.json.stages.schema` | Missing mandatory fields; type mismatch; unexpected columns | Use ASIM tester details; distinguish error, warning, and info |
| Data | `report.json.stages.data` | Invalid enumerations, formats, aliases, or values | Report failing field, value, and expected ASIM rule |
| Raw DCR | `qtpSourceReplay`, `rawDcr` | Raw table/DCR cannot be established | Warning-only when establishment fails; QTP/parity become blocked |
| Raw ingestion | `qtpSourceReplay`, upload/visibility evidence | Raw DCR exists but upload or visibility fails | This is a target failure when it runs and fails |
| QTP execution | `outputValidation`, error details | Query-time parser syntax/runtime failure | This is a target failure when it runs and fails |
| Parity | Complete QTP/ITP schemas and filtered rows | Shared type mismatch; row/value mismatch; duplicate-count mismatch | Compare shared columns; `Type` is intentionally excluded |
| Cleanup | `cleanup-result.json`, report evidence | DCR deletion failed or timed out | Report exact resource status without exposing credentials |

## Discovery signatures

### Zero targets

Check:

1. Was the workflow triggered only by a sample-data change?
2. Is the parser under exact `IngestTimeParsers` casing?
3. Does `changedParserPaths` omit a path present in the PR file list?
4. Does the path match:

   ```text
   Parsers/ASim*/IngestTimeParsers/*.yaml
   ```

Example:

```text
IngestTImeParsers   # invalid
IngestTimeParsers   # valid
```

### Non-static `EventVendor` or `EventProduct`

The resolver scans every exact field assignment and requires the right-hand
side to begin with a KQL string literal. It rejects:

```kusto
EventVendor = DeviceVendor
EventProduct = case(...)
EventProduct = ProductConstant
```

Repeated assignments are allowed only when every assignment uses the same
non-empty filename-safe literal. The resolver does not infer that a later
assignment overwrites an earlier one.

### Missing fixture

Use the exact error path. Common causes:

- No fixture added.
- `Fortigate` versus `FortiGate`.
- Product metadata differs from emitted `EventProduct`.
- Source table suffix or spaces differ.
- Fixture exists for another schema or table.

## Static validation signatures

| Finding | Meaning | Typical fix |
|---|---|---|
| `META*` | Required metadata, date, version, name, stream, source, or target is invalid | Correct the named YAML field |
| `SOURCE001` | Workspace parser does not use `InputStream: none` | Set the exact Workspace contract value |
| `FILTER*` | Filter query is not a valid ordered subset of parser row-selection logic | Preserve prerequisite calculations and predicate order |
| `FIXTURE*` | Fixture missing, malformed, or incompatible | Add/fix exact CSV and `Type` values |
| `KQL033` | An unsupported IP utility was detected | Use only functions allowed by current DCR validation |
| `KQL039`–`KQL043` | Query is not a valid single source-rooted contract | Remove external statements/subqueries and preserve one source pipeline |
| `KQL044` | Compacted transform exceeds Azure's limit | Remove comments/no-ops, simplify expressions, or reduce mappings without changing semantics |

A clean static result does not prove semantic compilation. Azure DCR creation
is the authoritative compile check.

## DCR compilation signatures

### Undefined symbol

Trace the column through operator order. `project`, `project-away`, and
`project-rename` can remove the original name.

Before:

```kusto
| project-rename EventOriginalUid = CrowdStrikeId
| extend EventUid = CrowdStrikeId
```

After:

```kusto
| project-rename EventOriginalUid = CrowdStrikeId
| extend EventUid = EventOriginalUid
```

### Invalid transform query

Preserve the complete nested Azure diagnostic. Check:

- Reported KQL line/column against the literal `ParserQuery`.
- DCR-supported operator/function set.
- Column availability after every projection/rename.
- Function argument types.
- Compact query length.

### Invalid stream

Check that `InputStream` is the stream that writes `SourceRawTable`, not merely
an incoming connector stream or the target ASIM output stream.

## Runtime and parity signatures

### Filtering count mismatch

- Canonicalize timestamps through Kusto ticks before comparing.
- Compare duplicate-aware counts by timestamp.
- Ensure filter prerequisites appear before the predicate.
- A pass-through filter must select every fixture row.

### Upload or visibility failure

Inspect:

- Input schema and explicit casts.
- Batch responses and accepted-row counts.
- Expected versus observed timestamps.
- Duplicate or missing rows.
- Table propagation delay versus hard rejection.

### Parity failure

Use:

- `qtp_schema`, `qtp_rows`
- `itp_schema`, `itp_rows`
- `intersect_schema`
- `qtp_rows_filtered`, `itp_rows_filtered`

First resolve shared-column type mismatches. Then compare typed, duplicate-aware
row multisets. Do not report the platform-managed `Type` difference as a parity
defect.

## Timeline and rerun checks

For every run:

1. Record run head SHA and start time.
2. Record current PR head SHA and latest commit time.
3. If they differ, inspect the run SHA.
4. State whether a later commit already fixes the observed issue.
5. Identify remaining failures expected in the next run.
