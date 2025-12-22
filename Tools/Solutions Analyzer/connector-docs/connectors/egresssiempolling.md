# Egress Iris Connector

| | |
|----------|-------|
| **Connector ID** | `EgressSiemPolling` |
| **Publisher** | Egress Software Technologies |
| **Tables Ingested** | [`DefendAuditData`](../tables-index.md#defendauditdata), [`EgressEvents_CL`](../tables-index.md#egressevents_cl) |
| **Used in Solutions** | [Egress Iris](../solutions/egress-iris.md) |
| **Connector Definition Files** | [EgressDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris/Data%20Connectors/EgressDataConnector.json) |

The Egress Iris connector will allow you to ingest Egress data into Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions on the Log Analytics workspace are required to enable the data connector.

**Custom Permissions:**
- **Egress API Token**: An Egress API token is required to ingest audit records to Microsoft Sentinel.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Egress Data with Microsoft Sentinel**

Enter your Egress API Hostname and secret.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
