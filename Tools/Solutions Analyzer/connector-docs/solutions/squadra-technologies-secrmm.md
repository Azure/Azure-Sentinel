# Squadra Technologies SecRmm

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Squadra Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.squadratechnologies.com/Contact.aspx](https://www.squadratechnologies.com/Contact.aspx) |
| **Categories** | domains |
| **First Published** | 2022-05-09 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Squadra Technologies secRMM](../connectors/squadratechnologiessecrmm.md)

**Publisher:** Squadra Technologies

Use the Squadra Technologies secRMM Data Connector to push USB removable storage security event data into Microsoft Sentinel Log Analytics.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow the step-by-step instructions provided in the [Squadra Technologies configuration guide for Azure Sentinel](https://www.squadratechnologies.com/StaticContent/ProductDownload/secRMM/9.11.0.0/secRMMAzureSentinelAdministratorGuide.pdf)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `secRMM_CL` |
| **Connector Definition Files** | [SquadraTechnologiesSecRMM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm/Data%20Connectors/SquadraTechnologiesSecRMM.json) |

[→ View full connector details](../connectors/squadratechnologiessecrmm.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `secRMM_CL` | [Squadra Technologies secRMM](../connectors/squadratechnologiessecrmm.md) |

[← Back to Solutions Index](../solutions-index.md)
