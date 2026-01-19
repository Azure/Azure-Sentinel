# Windows Firewall

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Windows Firewall](../connectors/windowsfirewall.md)

**Publisher:** Microsoft

### [Windows Firewall Events via AMA](../connectors/windowsfirewallama.md)

**Publisher:** Microsoft

Windows Firewall is a Microsoft Windows application that filters information coming to your system from the internet and blocking potentially harmful programs. The firewall software blocks most programs from communicating through the firewall. To stream your Windows Firewall application logs collected from your machines, use the Azure Monitor agent (AMA) to stream those logs to the Microsoft Sentinel workspace.



A configured data collection endpoint (DCE) is required to be linked with the data collection rule (DCR) created for the AMA to collect logs. For this connector, a DCE is automatically created in the same region as the workspace. If you already use a DCE stored in the same region, it's possible to change the default created DCE and use your existing one through the API. DCEs can be located in your resources with **SentinelDCE** prefix in the resource name.



For more information, see the following articles:

- [Data collection endpoints in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-endpoint-overview?tabs=portal)

- [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2228623&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci)

**Permissions:**

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule**

> Windows Firewall events are collected only from Windows agents.
- Configure WindowsFirewallAma data connector

- **Create data collection rule**

| | |
|--------------------------|---|
| **Tables Ingested** | `ASimNetworkSessionLogs` |
| **Connector Definition Files** | [template_WindowsFirewallAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Data%20Connectors/template_WindowsFirewallAma.JSON) |

[→ View full connector details](../connectors/windowsfirewallama.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimNetworkSessionLogs` | [Windows Firewall Events via AMA](../connectors/windowsfirewallama.md) |
| `WindowsFirewall` | [Windows Firewall](../connectors/windowsfirewall.md) |

[← Back to Solutions Index](../solutions-index.md)
