# Squadra Technologies secRMM

| | |
|----------|-------|
| **Connector ID** | `SquadraTechnologiesSecRMM` |
| **Publisher** | Squadra Technologies |
| **Tables Ingested** | [`secRMM_CL`](../tables-index.md#secrmm_cl) |
| **Used in Solutions** | [Squadra Technologies SecRmm](../solutions/squadra-technologies-secrmm.md) |
| **Connector Definition Files** | [SquadraTechnologiesSecRMM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm/Data%20Connectors/SquadraTechnologiesSecRMM.json) |

Use the Squadra Technologies secRMM Data Connector to push USB removable storage security event data into Microsoft Sentinel Log Analytics.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow the step-by-step instructions provided in the [Squadra Technologies configuration guide for Azure Sentinel](https://www.squadratechnologies.com/StaticContent/ProductDownload/secRMM/9.11.0.0/secRMMAzureSentinelAdministratorGuide.pdf)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
