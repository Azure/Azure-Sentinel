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

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Cisco Meraki REST API Key**: Enable API access in Cisco Meraki and generate API Key. Please refer to Cisco Meraki official [documentation](https://aka.ms/ciscomerakiapikey) for more information.
- **Cisco Meraki Organization Id**: Obtain your Cisco Meraki organization id to fetch security events. Follow the steps in the [documentation](https://aka.ms/ciscomerakifindorg) to obtain the Organization Id using the Meraki API Key obtained in previous step.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Cisco Meraki Security Events to Microsoft Sentinel**

To enable Cisco Meraki Security Events for Microsoft Sentinel, provide the required information below and click on Connect.
>This data connector depends on a parser based on a Kusto Function to render the content. [**CiscoMeraki**](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/CiscoMeraki/Parsers/CiscoMeraki.txt) Parser currently support only "**IDS Alert**" and "**File Scanned**" Events.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
