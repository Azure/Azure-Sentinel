# Cisco Meraki (using REST API)

| | |
|----------|-------|
| **Connector ID** | `CiscoMerakiNativePoller` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CiscoMerakiNativePoller_CL`](../tables-index.md#ciscomerakinativepoller_cl), [`meraki_CL`](../tables-index.md#meraki_cl) |
| **Used in Solutions** | [CiscoMeraki](../solutions/ciscomeraki.md) |
| **Connector Definition Files** | [azuredeploy_Cisco_Meraki_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Data%20Connectors/CiscoMerakiNativePollerConnector/azuredeploy_Cisco_Meraki_native_poller_connector.json) |

The [Cisco Meraki](https://aka.ms/ciscomeraki) connector allows you to easily connect your Cisco Meraki MX [security events](https://aka.ms/ciscomerakisecurityevents) to Microsoft Sentinel. The data connector uses [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.



 **Supported ASIM schema:** 

 1. Network Session

[← Back to Connectors Index](../connectors-index.md)
