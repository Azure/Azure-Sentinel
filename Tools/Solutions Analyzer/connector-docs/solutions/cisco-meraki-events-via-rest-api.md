# Cisco Meraki Events via REST API

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Meraki%20Events%20via%20REST%20API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Meraki%20Events%20via%20REST%20API) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md)

**Publisher:** Microsoft

The [Cisco Meraki](https://aka.ms/ciscomeraki) connector allows you to easily connect your Cisco Meraki organization events (Security events, Configuration Changes and API Requests) to Microsoft Sentinel. The data connector uses the [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) to fetch logs and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received data and ingests into ASIM and custom tables in your Log Analytics workspace. This data connector benefits from capabilities such as DCR based ingestion-time filtering, data normalization.



 **Supported ASIM schema:** 

 1. Network Session 

 2. Web Session  

 3. Audit Event

| | |
|--------------------------|---|
| **Tables Ingested** | `ASimAuditEventLogs` |
| | `ASimNetworkSessionLogs` |
| | `ASimWebSessionLogs` |
| **Connector Definition Files** | [dataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Meraki%20Events%20via%20REST%20API/Data%20Connectors/CiscoMerakiMultiRule_ccp/dataConnectorDefinition.json) |

[→ View full connector details](../connectors/ciscomerakimultirule.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuditEventLogs` | [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md) |
| `ASimNetworkSessionLogs` | [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md) |
| `ASimWebSessionLogs` | [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md) |

[← Back to Solutions Index](../solutions-index.md)
