# [Deprecated] Barracuda Web Application Firewall via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `Barracuda` |
| **Publisher** | Barracuda |
| **Tables Ingested** | [`Barracuda_CL`](../tables-index.md#barracuda_cl), [`CommonSecurityLog`](../tables-index.md#commonsecuritylog), [`barracuda_CL`](../tables-index.md#barracuda_cl) |
| **Used in Solutions** | [Barracuda WAF](../solutions/barracuda-waf.md) |
| **Connector Definition Files** | [template_Barracuda.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF/Data%20Connectors/template_Barracuda.json) |

The Barracuda Web Application Firewall (WAF) connector allows you to easily connect your Barracuda logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.



[For more information >​](https://aka.ms/CEF-Barracuda)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect Barracuda WAF**

The Barracuda Web Application Firewall can integrate with and export logs directly to Microsoft Sentinel via Azure OMS Server.​

1.  Go to [Barracuda WAF configuration](https://aka.ms/asi-barracuda-connector), and follow the instructions, using the parameters below to set up the connection:.

2.  Web Firewall logs facility: Go to the advanced settings (link below) for your workspace and on the **Data > Syslog** tabs, make sure that the facility exists.​

> Notice that the data from all regions will be stored in the selected workspace
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Open Syslog settings**

[← Back to Connectors Index](../connectors-index.md)
