# InfoSecGlobal Data Connector

| | |
|----------|-------|
| **Connector ID** | `InfoSecDataConnector` |
| **Publisher** | InfoSecGlobal |
| **Tables Ingested** | [`InfoSecAnalytics_CL`](../tables-index.md#infosecanalytics_cl) |
| **Used in Solutions** | [AgileSec Analytics Connector](../solutions/agilesec-analytics-connector.md) |
| **Connector Definition Files** | [Connector_Analytics_InfoSec.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AgileSec%20Analytics%20Connector/Data%20Connectors/Connector_Analytics_InfoSec.json) |

Use this data connector to integrate with InfoSec Crypto Analytics and get data sent directly to Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. InfoSecGlobal Crypto Analytics Data Connector**

1. Data is sent to Microsoft Sentinel through Logstash
 2. Required Logstash configuration is included with Crypto Analytics installation
 3. Documentation provided with the Crypto Analytics installation explains how to enable sending data to Microsoft Sentinel
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
