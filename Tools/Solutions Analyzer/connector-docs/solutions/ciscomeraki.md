# CiscoMeraki

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Cisco Meraki](../connectors/ciscomeraki.md)

**Publisher:** Cisco

### [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md)

**Publisher:** Microsoft

The [Cisco Meraki](https://aka.ms/ciscomeraki) connector allows you to easily connect your Cisco Meraki MX [security events](https://aka.ms/ciscomerakisecurityevents) to Microsoft Sentinel. The data connector uses [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.



 **Supported ASIM schema:** 

 1. Network Session

| | |
|--------------------------|---|
| **Tables Ingested** | `CiscoMerakiNativePoller_CL` |
| | `meraki_CL` |
| **Connector Definition Files** | [azuredeploy_Cisco_Meraki_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Data%20Connectors/CiscoMerakiNativePollerConnector/azuredeploy_Cisco_Meraki_native_poller_connector.json) |

[→ View full connector details](../connectors/ciscomerakinativepoller.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CiscoMerakiNativePoller_CL` | [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md) |
| `meraki_CL` | [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md), [[Deprecated] Cisco Meraki](../connectors/ciscomeraki.md) |

[← Back to Solutions Index](../solutions-index.md)
