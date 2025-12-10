# Azure CloudNGFW By Palo Alto Networks

| | |
|----------|-------|
| **Connector ID** | `AzureCloudNGFWByPaloAltoNetworks` |
| **Publisher** | Palo Alto Networks |
| **Tables Ingested** | [`fluentbit_CL`](../tables-index.md#fluentbit_cl) |
| **Used in Solutions** | [Azure Cloud NGFW by Palo Alto Networks](../solutions/azure-cloud-ngfw-by-palo-alto-networks.md) |
| **Connector Definition Files** | [CloudNgfwByPAN.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cloud%20NGFW%20by%20Palo%20Alto%20Networks/Data%20Connectors/CloudNgfwByPAN.json) |

Cloud Next-Generation Firewall by Palo Alto Networks - an Azure Native ISV Service - is Palo Alto Networks Next-Generation Firewall (NGFW) delivered as a cloud-native service on Azure. You can discover Cloud NGFW in the Azure Marketplace and consume it in your Azure Virtual Networks (VNet). With Cloud NGFW, you can access the core NGFW capabilities such as App-ID, URL filtering based technologies. It provides threat prevention and detection through cloud-delivered security services and threat prevention signatures. The connector allows you to easily connect your Cloud NGFW logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities. For more information, see the [Cloud NGFW for Azure documentation](https://docs.paloaltonetworks.com/cloud-ngfw/azure).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Cloud NGFW by Palo Alto Networks to Microsoft Sentinel**

Enable Log Settings on All Cloud NGFWs by Palo Alto Networks.
- Configure log settings: OpenCloudNGFW

Inside your Cloud NGFW resource:

1.  Navigate to the **Log Settings** from the homepage.
2.  Ensure the **Enable Log Settings** checkbox is checked.
3.  From the **Log Settings** drop-down, choose the desired Log Analytics Workspace.
4.  Confirm your selections and configurations.
5.  Click **Save** to apply the settings.

[← Back to Connectors Index](../connectors-index.md)
