# Fivetran - Microsoft Sentinel Solution

Ingests Fivetran platform and connector logs into a DCR-based custom table
(`Fivetran_CL`) in Microsoft Sentinel using the Azure Monitor
**Logs Ingestion API**. Fivetran PUSHES its logs to the Data Collection Rule
using an Entra ID app registration; nothing polls Fivetran.

## Contents

| Artifact | File |
| --- | --- |
| Custom table (ARM) | `Data Connectors/Fivetran_CCF/Fivetran_Table.json` |
| Data Collection Rule (ARM) | `Data Connectors/Fivetran_CCF/Fivetran_DCR.json` |
| Data connector tile | `Data Connectors/Fivetran_CCF/Fivetran_DataConnector.json` |
| Parser (KQL function `Fivetran`) | `Parsers/Fivetran.yaml` |
| Analytics rule - ingestion gap (Defense Evasion / T1562) | `Analytic Rules/FivetranIngestionGap.yaml` |
| Analytics rule - auth failures (Credential Access / T1110) | `Analytic Rules/FivetranAuthFailures.yaml` |
| Hunting query - SEVERE spike | `Hunting Queries/FivetranSevereSpike.yaml` |
| Overview workbook (includes volume and cost panels) | `Workbooks/Fivetran.json` |
| Solution manifest | `Data/Solution_Fivetran.json` |
| Publisher metadata | `SolutionMetadata.json` |
| Change history | `ReleaseNotes.md` |
| Volume and cost guidance (optional) | `VOLUME-AND-COST.md` |
| Split-plan DCR variant (optional) | `Data Connectors/Fivetran_CCF/Fivetran_DCR_SplitPlan.json` |
| Auxiliary plan verbose table (optional) | `Data Connectors/Fivetran_CCF/FivetranVerbose_Table.json` |

## Deployment order

1. Deploy `Fivetran_Table.json` and `Fivetran_DCR.json`. The data connector
   tile's instruction steps cover the Entra ID app registration, Data Collection
   Endpoint and `Monitoring Metrics Publisher` RBAC assignment on the DCR.
2. Configure Fivetran's external-log (Azure Monitor) connector in Logs Ingestion
   API mode with the DCR values.
3. Install the parser, analytics rule, hunting query and workbook (bundled when
   the solution is packaged - see `PACKAGING.md`).

## Design note - push, not poll

This is a push feed, so the solution deliberately has **no** `PollingConfig.json`
and **no** CCF `DataConnectorDefinition.json` (kind Customizable). The connector
tile is a classic status/documentation connector whose connection state is
computed by a KQL `IsConnectedQuery` against the custom table. Data movement is
performed by Fivetran plus the DCR, not by Sentinel.

## Alternative connection paths

The shipped solution above is the real-time push feed (External Logs -> DCR ->
`Fivetran_CL`). For the structured Fivetran **Platform Connector** audit data (the
full `AUDIT_TRAIL` and metadata tables, which are not carried by the External Logs
feed), a self-contained reference build is provided under
[`Platform-Connector-Ingest/`](Platform-Connector-Ingest/README.md): an Event Grid
triggered Azure Function reads the lake parquet and ingests it into typed Sentinel
tables (`Fivetran_AuditTrail_CL`, `Fivetran_Platform_CL`), with an ASIM AuditEvent
parser and hunting query. It is documented IaC (not part of this Content Hub package)
because it depends on a customer-owned ADLS Gen2 lake.

## ASIM normalization

ASIM parsers are not part of this solution package. They are contributed to the
shared `Parsers/ASimAuditEvent/Parsers/` and
`Parsers/ASimAuthentication/Parsers/` folders so the `Im*` and
`imAuditEvent` union parsers pick them up.

## Managing log volume and cost (optional)

The External Logs feed is dominated by routine `INFO` connector sync messages,
which carry little detection value. If that volume is a problem, `VOLUME-AND-COST.md`
covers four options: DCR-level filtering, a split across the Analytics and
Auxiliary table plans using the optional `Fivetran_DCR_SplitPlan.json` and
`FivetranVerbose_Table.json`, shorter retention, and using the Platform Connector
path instead.

The workbook's "Ingestion volume and cost" section shows where your volume
actually sits before you change anything. The `FivetranIngestionGap` analytics
rule is deliberately tier-agnostic (`union isfuzzy=true` across `Fivetran_CL` and
the optional `FivetranVerboseSummary_CL`), so it works correctly in both the
default and split deployments.

The default deployment is unchanged and remains a single Analytics plan table.

## Prerequisites (customer)
- Log Analytics workspace with Microsoft Sentinel enabled.
- Entra ID app registration (Client ID, Client Secret, Tenant ID).
- `Monitoring Metrics Publisher` role for that app on the DCR.
