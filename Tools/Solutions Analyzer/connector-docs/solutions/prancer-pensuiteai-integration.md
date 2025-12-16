# Prancer PenSuiteAI Integration

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Prancer PenSuiteAI Integration |
| **Support Tier** | Partner |
| **Support Link** | [https://www.prancer.io](https://www.prancer.io) |
| **Categories** | domains |
| **First Published** | 2023-08-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Prancer Data Connector](../connectors/prancerlogdata.md)

**Publisher:** Prancer

The Prancer Data Connector has provides the capability to ingest Prancer (CSPM)[https://docs.prancer.io/web/CSPM/] and [PAC](https://docs.prancer.io/web/PAC/introduction/) data to process through Microsoft Sentinel. Refer to [Prancer Documentation](https://docs.prancer.io/web) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Include custom pre-requisites if the connectivity requires - else delete customs**: Description for any custom pre-requisite

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Prancer REST API to pull logs into Microsoft sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

STEP 1: Follow the documentation on the [Prancer Documentation Site](https://docs.prancer.io/web/) in order to set up an scan with an azure cloud connector.

STEP 2: Once the scan is created go to the 'Third Part Integrations' menu for the scan and select Sentinel.

STEP 3: Create follow the configuration wizard to select where in Azure the results should be sent to.

STEP 4: Data should start to get fed into Microsoft Sentinel for processing.

| | |
|--------------------------|---|
| **Tables Ingested** | `prancer_CL` |
| **Connector Definition Files** | [PrancerLogData.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Data%20Connectors/PrancerLogData.json) |

[→ View full connector details](../connectors/prancerlogdata.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `prancer_CL` | [Prancer Data Connector](../connectors/prancerlogdata.md) |

[← Back to Solutions Index](../solutions-index.md)
