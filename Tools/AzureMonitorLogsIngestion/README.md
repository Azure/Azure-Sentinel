# Azure Monitor Logs Ingestion

This tool ingests JSON mock data into a Log Analytics workspace through the
Azure Monitor Logs Ingestion API. It can create and reuse a Data Collection
Endpoint (DCE) and Data Collection Rule (DCR) for:

- custom `_CL` tables; and
- Microsoft standard tables that Azure supports as DCR output streams.

Both modes send records to a declared `Custom-*` input stream. For a standard
table, the DCR transform maps that writable input to a supported
`Microsoft-*` output stream. The tool never posts directly to a reserved
Microsoft stream.

## Install

Use Python 3.10 or later and sign in with Azure CLI:

```powershell
az login
az account set --subscription "<subscription>"
python -m pip install -e Tools\AzureMonitorLogsIngestion
azure-monitor-logs-ingestion doctor
```

`DefaultAzureCredential` is used, so managed identity and other supported
credential sources can also be used. No client secret is stored by this tool.

Permissions are operation-specific. The caller needs workspace/resource read
access to inspect the locked target; DCR creation permission only when the
selected plan provisions a contract-specific DCR; and table-write permission
only when the required custom destination table is absent. DCE creation is
conditional: Azure Monitor generally needs a DCE for private-link ingestion or
when a DCR has no ingestion endpoint, although this tool may provision an
isolated DCE as part of its supported contract route. Do not treat DCE creation
as a universal Logs Ingestion API requirement. The identity that sends data
also needs **Monitoring Metrics Publisher** on the DCR for telemetry write.
Report an uninspectable permission as unknown, not granted.

## Contract

Start with:

- `examples\custom-table.yaml` for a custom table; or
- `examples\standard-table.yaml` for a supported standard table.

`ingestion-contract.schema.json` contains the versioned JSON Schema for editor
and CI validation.

The contract separates the raw mock-data schema from the destination:

```yaml
version: 1
name: sample-common-security-log
workspace: my-workspace
inputStream: Custom-CommonSecurityLogMock
inputColumns:
  - name: EventTime
    type: datetime
transformKql: source | project TimeGenerated=todatetime(EventTime)
destination:
  kind: standard
  table: CommonSecurityLog
  outputStream: Microsoft-CommonSecurityLog
```

Raw input field names may use vendor-native dots and hyphens, such as
`event.timestamp` or `cs-username`. Reference those fields with KQL bracket
notation in the transform, for example `tostring(['cs-username'])`. Destination
column names remain restricted to valid Log Analytics identifiers.

For custom destinations, provide the complete destination schema and use
`Custom-<TableName>` as `outputStream`. Custom table names must end in `_CL`.

For standard destinations, the table must already be registered in the
workspace. Azure is the authority on whether the `Microsoft-*` output stream
supports Logs Ingestion. If it does not, DCR provisioning fails with the Azure
error, commonly `InvalidStream`; the tool does not redirect data elsewhere.

Transforms should explicitly cast and project only columns accepted by the
destination table.

Reviewed Standard-table capabilities live in `registry.yaml`; each registry
entry points to a versioned contract template under `contracts\`, declares
the supported writable route, and links to public schema and API evidence.
Only registered tables are eligible for automatic qualification plans.
`CommonSecurityLog.yaml` is a structured-field contract for the fields used by
the current Cisco ASA scenarios; it is not a raw CEF parser and does not prove
that a connector, parser, or deployed DCR is configured correctly. The listed
schema derives from the public CommonSecurityLog table reference and public
Log Analytics metadata endpoint. System-managed/reserved table columns are
intentionally not included as writable fixture fields.

The public table-feature matrix distinguishes DCR transformation support from
Logs Ingestion API support. Registration requires both an explicit reviewed
contract/transform and a documented supported output route. The public
metadata endpoint can inform schema validation, but its existence or the
presence of a table in that catalog is not sufficient evidence that a route
is writable. `liveValidated: false` remains until a live, approved test
validates the exact contract against the selected workspace.

Resolve and print a deterministic plan without Azure access or writes:

```powershell
azure-monitor-logs-ingestion resolve `
  --table CommonSecurityLog `
  --required-field DeviceEventClassID:string `
  --required-field SourceIP `
  --report "<run-evidence-folder>\ingestion-resolution.json"
```

The resolver reports the registered schema/transform fingerprints and a
provision-or-reuse plan. Unknown tables and fields outside the contract are
blocked rather than guessed. To read only the exact candidates in the locked
workspace, pass its ARM ID and `--check-existing`:

```powershell
azure-monitor-logs-ingestion resolve `
  --table CommonSecurityLog `
  --required-field DeviceEventClassID:string `
  --workspace "<locked-workspace-arm-id>" `
  --check-existing `
  --report "<run-evidence-folder>\ingestion-resolution.json"
```

This mode checks the existing standard table schema and only the contract's
exact DCE/DCR names. It never lists workspaces, scans resource groups, or
creates/updates resources. An existing DCE/DCR pair is reusable only when
ownership tags, input schema, transform, output stream, endpoint, and locked
workspace all match. A mismatched or partial resource pair is blocked for
manual review. A compatible missing-resource result is still only a plan and
does not constitute write approval. Resolution report paths are also
create-only; use a new filename to preserve earlier evidence.

Generated contracts keep `workspace: qualification-target`; apply the locked
lab workspace without editing the file:

```powershell
azure-monitor-logs-ingestion run `
  --contract "<scenario-folder>\ingestion-contract.yaml" `
  --workspace "<workspace-arm-id>" `
  --payload "<scenario-folder>\mock.json"
```

For a solution-wide Qualification plan, enumerate every recursive source
Analytic Rule and pair it to its converted Custom Detection before generating
rule-specific fixtures. For a partial package, keep that complete inventory
for accounting but plan only the selected, validated pairs by supplying the
fresh applied selection plan and hash:

```powershell
python Tools\SolutionMigration\resolve_ingestion_contracts.py `
  --solution "Solutions\<solution>" `
  --target-context "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json" `
  --selection-plan "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\package-selection-plan.json" `
  --expected-selection-plan-sha256 "<current-applied-plan-sha256>" `
  --output "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\<version>\ingestion-contract-plan.json"
```

The plan groups rules only when their registered table schema/transform
fingerprints match, and records rule/detection file and query hashes plus the
exact locked target. Partial selection still reports the original full
inventory, selected scope, coverage, and excluded rule identities/reasons; it
does not mark unselected rules as qualified. The applied selection must satisfy
the canonical strict over-50% validated migrated-detection threshold. The plan
performs no Azure calls or writes and does not generate scenarios. Before write
approval, rerun with the original plan's
`--expected-inventory-sha256` and `--expected-target-sha256`; a changed source
inventory, target, or applied selection returns `stale-plan`. Select a new
output path for each plan; existing plan files are never overwritten.

Adding a registered table requires a reviewed writable input schema,
destination schema, deterministic transform, Microsoft output stream,
isolated DCE/DCR names, public schema and route references, tests, and live
validation before setting `liveValidated: true`.

The Log Analytics query SDK is not a source of DCR transformations. It
executes queries; DCR `transformKql` is customer-visible resource
configuration and must be read from or compared against the exact DCR through
the ARM resource surface. The resolver does not seek hidden service-side
transforms.

## Ingest mock data

Validate locally:

```powershell
azure-monitor-logs-ingestion inspect `
  --contract .\contract.yaml `
  --payload .\mock.json
```

Provision and ingest:

```powershell
azure-monitor-logs-ingestion run `
  --contract .\contract.yaml `
  --workspace "<optional-workspace-name-or-arm-id-override>" `
  --payload .\mock.json
```

The command writes `ingestion-report.json` beside the payload by default. Use
`--report <path>` to choose another location.

The default DCE and DCR names are derived from `name`. Keep those names unique
per ingestion contract. The tool tags new resources with both `managed-by` and
`ingestion-contract`.

Existing resources are updated only when they are owned by this tool and the
DCR already contains exactly the requested input stream. The tool does not add
a new stream to an existing DCR. Azure can expose later stream additions in ARM
while the Logs Ingestion endpoint continues to reject them against the DCR's
immutable ID. Use a separate contract-specific DCE/DCR pair instead.

A name collision with an unrelated resource, a different ingestion contract,
or a shared DCR fails safely. Change `resources.dce` and `resources.dcr` in the
contract rather than overwriting or extending the existing resources.

Optionally grant a service principal or managed identity permission while
provisioning:

```powershell
azure-monitor-logs-ingestion run `
  --contract .\contract.yaml `
  --payload .\mock.json `
  --principal-id "<entra-object-id>" `
  --principal-type ServicePrincipal
```

`--principal-id` is an Entra object ID, not an application/client ID. A user
can be assigned with `--principal-type User`.

The tool accepts a JSON array, a single JSON object, JSON Lines, or NDJSON. It
rejects undeclared fields and obvious JSON type mismatches before sending. It
creates batches below the one-megabyte Logs Ingestion API request limit and
retries throttled or transient requests.

## Separate operations

```powershell
azure-monitor-logs-ingestion provision --contract .\contract.yaml
azure-monitor-logs-ingestion ingest --contract .\contract.yaml --payload .\mock.json
azure-monitor-logs-ingestion verify --contract .\contract.yaml --lookback-minutes 60
```

Ingestion success means Azure accepted each batch. Processing is asynchronous.
If no fresh rows are visible, `verify` reports `status: pending` and exits with
code 1. Run it again after Azure finishes processing.

Use synthetic data and a non-production workspace. Do not commit credentials,
tenant identifiers, workspace identifiers, or customer telemetry.
