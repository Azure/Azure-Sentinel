# Egress Defend

| | |
|----------|-------|
| **Connector ID** | `EgressDefendPolling` |
| **Publisher** | Egress Software Technologies |
| **Tables Ingested** | [`EgressDefend_CL`](../tables-index.md#egressdefend_cl) |
| **Used in Solutions** | [Egress Defend](../solutions/egress-defend.md) |
| **Connector Definition Files** | [DefendAPIConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Data%20Connectors/DefendAPIConnector.json) |

The Egress Defend audit connector provides the capability to ingest Egress Defend Data into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions on the Log Analytics workspace are required to enable the data connector.

**Custom Permissions:**
- **Egress API Token**: An Egress API token is required to ingest audit records to Microsoft Sentinel.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Egress Defend with Microsoft Sentinel**

Enter your Egress Defend API URl, Egress Domain and API token.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
