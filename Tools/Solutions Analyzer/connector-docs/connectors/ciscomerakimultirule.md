# Cisco Meraki (using REST API)

| | |
|----------|-------|
| **Connector ID** | `CiscoMerakiMultiRule` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ASimAuditEventLogs`](../tables-index.md#asimauditeventlogs), [`ASimNetworkSessionLogs`](../tables-index.md#asimnetworksessionlogs), [`ASimWebSessionLogs`](../tables-index.md#asimwebsessionlogs) |
| **Used in Solutions** | [Cisco Meraki Events via REST API](../solutions/cisco-meraki-events-via-rest-api.md) |
| **Connector Definition Files** | [dataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Meraki%20Events%20via%20REST%20API/Data%20Connectors/CiscoMerakiMultiRule_ccp/dataConnectorDefinition.json) |

The [Cisco Meraki](https://aka.ms/ciscomeraki) connector allows you to easily connect your Cisco Meraki organization events (Security events, Configuration Changes and API Requests) to Microsoft Sentinel. The data connector uses the [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) to fetch logs and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received data and ingests into ASIM and custom tables in your Log Analytics workspace. This data connector benefits from capabilities such as DCR based ingestion-time filtering, data normalization.



 **Supported ASIM schema:** 

 1. Network Session 

 2. Web Session  

 3. Audit Event

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Cisco Meraki REST API Key**: Enable API access in Cisco Meraki and generate API Key. Please refer to Cisco Meraki official [documentation](https://aka.ms/ciscomerakiapikey) for more information.
- **Cisco Meraki Organization Id**: Obtain your Cisco Meraki organization id to fetch security events. Follow the steps in the [documentation](https://aka.ms/ciscomerakifindorg) to obtain the Organization Id using the Meraki API Key obtained in previous step.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Cisco Meraki events to Microsoft Sentinel**

Currently, this connector allows to ingest events from the following [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) endpoint: 
 1. [Get Organization Appliance Security Events](https://developer.cisco.com/meraki/api-latest/#!get-organization-appliance-security-events) 
>This connector parses **IDS Alert** events into ASimNetworkSessionLogs Table and **File Scanned** events into ASimWebSessionLogs Table. 
 2. [Get Organization Api Requests](https://developer.cisco.com/meraki/api-latest/#!get-organization-api-requests) 
>This connector parses events into ASimWebSessionLogs Table. 
 3. [Get Organization Configuration Changes](https://developer.cisco.com/meraki/api-latest/#!get-organization-configuration-changes) 
>This connector parses events into ASimAuditEventLogs Table.
- **Organization Id**: OrganizationId
- **API Key**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
