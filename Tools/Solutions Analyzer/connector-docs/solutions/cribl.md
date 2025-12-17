# Cribl

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cribl |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cribl.io/support/](https://www.cribl.io/support/) |
| **Categories** | domains |
| **First Published** | 2024-08-01 |
| **Last Updated** | 2024-09-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cribl](../connectors/cribl.md)

**Publisher:** Cribl

The [Cribl](https://cribl.io/accelerate-cloud-migration/) connector allows you to easily connect your Cribl (Cribl Enterprise Edition - Standalone) logs with Microsoft Sentinel. This gives you more security insight into your organization's data pipelines.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Installation and setup instructions for Cribl Stream for Microsoft Sentinel**

Use the documentation from this Github repository and configure Cribl Stream using 

https://docs.cribl.io/stream/usecase-azure-workspace/

| | |
|--------------------------|---|
| **Tables Ingested** | `CriblAccess_CL` |
| | `CriblAudit_CL` |
| | `CriblInternal_CL` |
| | `CriblUIAccess_CL` |
| **Connector Definition Files** | [Connector_Cribl.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl/Data%20Connectors/Connector_Cribl.json) |

[→ View full connector details](../connectors/cribl.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CriblAccess_CL` | [Cribl](../connectors/cribl.md) |
| `CriblAudit_CL` | [Cribl](../connectors/cribl.md) |
| `CriblInternal_CL` | [Cribl](../connectors/cribl.md) |
| `CriblUIAccess_CL` | [Cribl](../connectors/cribl.md) |

[← Back to Solutions Index](../solutions-index.md)
