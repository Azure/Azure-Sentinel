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

The caller needs permission to read the workspace and create or update tables,
DCEs, and DCRs in the workspace resource group. The identity that sends data
also needs the **Monitoring Metrics Publisher** role on the DCR.

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

Reviewed Standard-table contracts live under `contracts\`. Only tables in that
registry are eligible for automatic qualification provisioning. Generated
contracts keep `workspace: qualification-target`; apply the locked lab
workspace without editing the file:

```powershell
azure-monitor-logs-ingestion run `
  --contract "<scenario-folder>\ingestion-contract.yaml" `
  --workspace "<workspace-arm-id>" `
  --payload "<scenario-folder>\mock.json"
```

Adding a registered table requires a reviewed writable input schema,
transform, Microsoft output stream, isolated DCE/DCR names, and live
validation.

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
