# Windows Firewall Events via AMA

| | |
|----------|-------|
| **Connector ID** | `WindowsFirewallAma` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ASimNetworkSessionLogs`](../tables-index.md#asimnetworksessionlogs) |
| **Used in Solutions** | [Windows Firewall](../solutions/windows-firewall.md) |
| **Connector Definition Files** | [template_WindowsFirewallAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Data%20Connectors/template_WindowsFirewallAma.JSON) |

Windows Firewall is a Microsoft Windows application that filters information coming to your system from the internet and blocking potentially harmful programs. The firewall software blocks most programs from communicating through the firewall. To stream your Windows Firewall application logs collected from your machines, use the Azure Monitor agent (AMA) to stream those logs to the Microsoft Sentinel workspace.



A configured data collection endpoint (DCE) is required to be linked with the data collection rule (DCR) created for the AMA to collect logs. For this connector, a DCE is automatically created in the same region as the workspace. If you already use a DCE stored in the same region, it's possible to change the default created DCE and use your existing one through the API. DCEs can be located in your resources with **SentinelDCE** prefix in the resource name.



For more information, see the following articles:

- [Data collection endpoints in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-endpoint-overview?tabs=portal)

- [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2228623&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci)

[← Back to Connectors Index](../connectors-index.md)
