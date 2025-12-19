# SINEC Security Guard

| | |
|----------|-------|
| **Connector ID** | `SSG` |
| **Publisher** | Siemens AG |
| **Tables Ingested** | [`SINECSecurityGuard_CL`](../tables-index.md#sinecsecurityguard_cl) |
| **Used in Solutions** | [SINEC Security Guard](../solutions/sinec-security-guard.md) |
| **Connector Definition Files** | [data_connector_GenericUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard/Data%20Connectors/data_connector_GenericUI.json) |

The SINEC Security Guard solution for Microsoft Sentinel allows you to ingest security events of your industrial networks from the [SINEC Security Guard](https://siemens.com/sinec-security-guard) into Microsoft Sentinel

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

This Data Connector relies on the SINEC Security Guard Sensor Package to be able to receive Sensor events in Microsoft Sentinel. The Sensor Package can be purchased in the Siemens Xcelerator Marketplace.
**1. Please follow the steps to configure the data connector**

**Set up the SINEC Security Guard Sensor**

  Detailed step for setting up the sensor.

  **Create the Data Connector and configure it in the SINEC Security Guard web interface**

  Instructions on configuring the data connector.

[← Back to Connectors Index](../connectors-index.md)
