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

[← Back to Connectors Index](../connectors-index.md)
