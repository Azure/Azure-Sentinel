# Fivetran Platform Connector ingest (third connection path, + ASIM)

A push connector that ingests the **Fivetran Platform Connector** tables from the
Managed Data Lake (ADLS Gen2) into Microsoft Sentinel custom tables, then normalises
the security-relevant `audit_trail` table to **ASIM AuditEvent**.

This is a fully worked, deployable reference. It contains no customer-specific names,
resource ids, or subscription ids: every environment value is a `<placeholder>` you set
at deploy time.

## Where this fits: three ways to connect Fivetran to Sentinel

| # | Path | What it is | Best for |
| --- | --- | --- | --- |
| 1 | **External Logs -> DCR -> `Fivetran_CL`** | Fivetran pushes its platform/connector log stream straight into a DCR-based custom table. This is the connector shipped in the main `Solutions/Fivetran/` solution. | Real-time platform/connector monitoring and alerting. |
| 2 | **Platform Connector -> ADLS -> ADX external table** | Fivetran lands the full metadata + `AUDIT_TRAIL` tables as parquet in a lake; an ADX external table queries them on demand via `adx()`. | Long-retention compliance archive with no per-GB ingestion cost. |
| 3 | **Platform Connector -> ADLS -> Function -> Logs Ingestion -> Sentinel** (this folder) | An Event Grid triggered Azure Function reads the lake parquet and ingests the rows into typed Sentinel tables, normalising `audit_trail` to ASIM. | Native Analytics Rules, UEBA, entity mapping, and ASIM cross-source correlation over the audit data. |

Path 1 carries the platform/connector **log stream** but not the full, structured
**AUDIT_TRAIL** (several audit tables are not available through the External Logs
connector). The audit data only exists in the **Platform Connector -> ADLS parquet**.
This connector is how that structured audit data reaches Sentinel as a first-class,
detectable table.

## Source layout

The Fivetran Platform Connector lands 12 tables into the managed data lake, each as its
own Delta + Iceberg (UniForm) table under `<lake-root>/<schema>/<table>/`:

- `data/*.parquet` - the rows
- `_delta_log/` - Delta transaction log
- `metadata/*.metadata.json` + `*.avro` - Iceberg manifests
- `orphans/` - superseded files

```
audit_trail        <- security events (typed, ASIM AuditEvent)
user  team  team_membership  role  role_permission  role_connector_type
resource_membership  connection  destination  account  connector_type   <- reference/metadata
```

## Architecture

```
Fivetran Platform Connector  --(daily sync)-->  ADLS Gen2 (Delta+Iceberg parquet)
                                                        |
                                   Blob Created event on .../<table>/data/*.parquet
                                                        |
                                    Event Grid (subject filter + dead-letter)
                                                        |
                          Azure Function (Python, Flex Consumption, managed identity)
                                       reads parquet, routes by table
                                                        |
                         +------------------------------+-----------------------------+
                         | audit_trail (typed)                 | 11 reference tables  |
                         v                                     v                       |
             Custom-Fivetran_AuditTrail_CL          Custom-Fivetran_Platform_CL        |
                         \_____________ Logs Ingestion API ____________/               |
                                                        |
                                       DCR (kind: Direct, 2 streams + transforms)
                                                        |
                                  Fivetran_AuditTrail_CL       Fivetran_Platform_CL
                                                        |
                            ASimAuditEventFivetranAuditTrail (dedupe by id)  --> content
```

### Two tables, one DCR (design decision)

- **`Fivetran_AuditTrail_CL`** (typed) - the security events. Typed columns
  (`action`, `user_id`, `primary_resource_*`, `old_values`, `new_values`, ...) so
  detections and the ASIM parser are exact.
- **`Fivetran_Platform_CL`** (generic envelope: `FivetranTable`, `Record` dynamic) -
  the other 11 reference/metadata tables. These are dimension/lookup data (who is in
  which team/role, which connection maps to which destination), used to **enrich and
  join**, not to alert on. A generic envelope ingests all of them with one stream and
  survives Fivetran schema drift. Any table can be promoted to a typed table later if a
  detection needs typed columns.

### At-least-once + dedupe (Delta/Iceberg reality)

Delta/Iceberg **compaction rewrites data files**, which re-emits rows already ingested.
The connector is therefore deliberately **at-least-once**; correctness comes from
**deduping on the immutable primary key**, not from the transport:

- `audit_trail`: the ASIM parser `vimAuditEventFivetranAuditTrail` dedupes with
  `summarize arg_max(TimeGenerated, *) by id` before normalising, so every consumer gets
  de-duplicated rows automatically.
- reference tables: dedupe by the row id inside `Record` at query time, or build a
  materialized view keyed on it if you query them hot.

## ASIM normalisation

`audit_trail` is a genuine event stream, so it maps to **ASIM AuditEvent 0.1.2**:

| ASIM field | From AUDIT_TRAIL |
| --- | --- |
| EventStartTime / EventEndTime | `captured_at` |
| Operation / EventOriginalType | `action` |
| EventType | derived from `action` (Create/Delete/Set/Enable/Disable/Read/Other) |
| EventResult | `Success` (AUDIT_TRAIL records completed actions) |
| Object / ObjectType | `primary_resource_id` / `primary_resource_type` |
| OldValue / NewValue | `old_values` / `new_values` |
| ActorUserId / ActorUsername | `user_id` |
| AdditionalFields | `interaction_method`, `secondary_resource_*` |

The 11 reference tables are **not** ASIM events (they are dimension tables), so no ASIM
parser is shipped for them. They are the enrichment source (for example join
`ActorUserId` to the `user` table for an email address).

Parsers + consuming content live in `content/`:
- `vimAuditEventFivetranAuditTrail.yaml` - filtering parser (full ASIM audit params).
- `ASimAuditEventFivetranAuditTrail.yaml` - parameter-less parser.
- `FivetranAuditTrailSensitiveChanges_ASIM_Hunting.yaml` - hunting query that consumes
  the parser.

## Files

- `function/function_app.py` - Event Grid triggered Python function, routes 12 tables.
- `function/requirements.txt`, `host.json`, `local.settings.json.example`.
- `fivetran-platform-dcr.json` - DCR body (2 streams + transforms) for CLI use.
- `bicep/sentinel-tables-dcr.bicep` - tables + DCR + optional DCR role assignment
  (compile with `az bicep build`).
- `content/` - the ASIM parsers + consuming hunting query.
- `test/test_audittrail_parser.py` - offline dummy-data test of the parser mapping.
- `DEPLOYMENT-GUIDE.md` - end-to-end deploy runbook (Flex Consumption + managed identity).
- `IMPROVEMENTS.md` - what this reference improves versus a first-generation build.

## Quick start

See `DEPLOYMENT-GUIDE.md` for the full runbook. In short:

1. Deploy `bicep/sentinel-tables-dcr.bicep` to the Sentinel resource group (tables + DCR).
2. Create a user-assigned managed identity and pre-grant it the two roles.
3. Deploy the Flex Consumption function app with that identity; set the DCR app settings.
4. Create the Event Grid subscription (subject filtered, with dead-lettering).
5. Import the `content/` parsers and verify with the KQL in the guide.
