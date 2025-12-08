# Network Security Groups

| | |
|----------|-------|
| **Connector ID** | `AzureNSG` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureDiagnostics`](../tables-index.md#azurediagnostics) |
| **Used in Solutions** | [Azure Network Security Groups](../solutions/azure-network-security-groups.md) |
| **Connector Definition Files** | [AzureNSG.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Network%20Security%20Groups/Data%20Connectors/AzureNSG.JSON) |

Azure network security groups (NSG) allow you to filter network traffic to and from Azure resources in an Azure virtual network. A network security group includes rules that allow or deny traffic to a virtual network subnet, network interface, or both.



When you enable logging for an NSG, you can gather the following types of resource log information:



- **Event:** Entries are logged for which NSG rules are applied to VMs, based on MAC address.

- **Rule counter:** Contains entries for how many times each NSG rule is applied to deny or allow traffic. The status for these rules is collected every 300 seconds.





This connector lets you stream your NSG diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223718&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
