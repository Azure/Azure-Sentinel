# Azure Network Security Groups

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Network%20Security%20Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Network%20Security%20Groups) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Network Security Groups](../connectors/azurensg.md)

**Publisher:** Microsoft

Azure network security groups (NSG) allow you to filter network traffic to and from Azure resources in an Azure virtual network. A network security group includes rules that allow or deny traffic to a virtual network subnet, network interface, or both.



When you enable logging for an NSG, you can gather the following types of resource log information:



- **Event:** Entries are logged for which NSG rules are applied to VMs, based on MAC address.

- **Rule counter:** Contains entries for how many times each NSG rule is applied to deny or allow traffic. The status for these rules is collected every 300 seconds.





This connector lets you stream your NSG diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223718&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureNSG.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Network%20Security%20Groups/Data%20Connectors/AzureNSG.JSON) |

[→ View full connector details](../connectors/azurensg.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Network Security Groups](../connectors/azurensg.md) |

[← Back to Solutions Index](../solutions-index.md)
