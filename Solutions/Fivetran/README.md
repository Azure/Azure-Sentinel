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
| ASIM Authentication parser (parameterless) | `Parsers/ASimAuthenticationFivetran.yaml` |
| ASIM Authentication parser (filtering) | `Parsers/vimAuthenticationFivetran.yaml` |
| ASIM AuditEvent parser (parameterless) | `Parsers/ASimAuditEventFivetran.yaml` |
| ASIM AuditEvent parser (filtering) | `Parsers/vimAuditEventFivetran.yaml` |
| Analytics rule - ingestion gap (Defense Evasion / T1562) | `Analytic Rules/FivetranIngestionGap.yaml` |
| Analytics rule - auth failures (Credential Access / T1110) | `Analytic Rules/FivetranAuthFailures.yaml` |
| Hunting query - SEVERE spike | `Hunting Queries/FivetranSevereSpike.yaml` |
| Overview workbook | `Workbooks/Fivetran.json` |
| Solution manifest | `Data/Solution_Fivetran.json` |
| Publisher metadata | `SolutionMetadata.json` |
| Change history | `ReleaseNotes.md` |

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

## Prerequisites (customer)

- Log Analytics workspace with Microsoft Sentinel enabled.
- Entra ID app registration (Client ID, Client Secret, Tenant ID).
- `Monitoring Metrics Publisher` role for that app on the DCR.
