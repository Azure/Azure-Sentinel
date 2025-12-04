# Azure Cloud NGFW by Palo Alto Networks

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Palo Alto Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://support.paloaltonetworks.com](https://support.paloaltonetworks.com) |
| **Categories** | domains |
| **First Published** | 2023-11-03 |
| **Last Updated** | 2023-11-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cloud%20NGFW%20by%20Palo%20Alto%20Networks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cloud%20NGFW%20by%20Palo%20Alto%20Networks) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure CloudNGFW By Palo Alto Networks](../connectors/azurecloudngfwbypaloaltonetworks.md)

**Publisher:** Palo Alto Networks

Cloud Next-Generation Firewall by Palo Alto Networks - an Azure Native ISV Service - is Palo Alto Networks Next-Generation Firewall (NGFW) delivered as a cloud-native service on Azure. You can discover Cloud NGFW in the Azure Marketplace and consume it in your Azure Virtual Networks (VNet). With Cloud NGFW, you can access the core NGFW capabilities such as App-ID, URL filtering based technologies. It provides threat prevention and detection through cloud-delivered security services and threat prevention signatures. The connector allows you to easily connect your Cloud NGFW logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities. For more information, see the [Cloud NGFW for Azure documentation](https://docs.paloaltonetworks.com/cloud-ngfw/azure).

| | |
|--------------------------|---|
| **Tables Ingested** | `fluentbit_CL` |
| **Connector Definition Files** | [CloudNgfwByPAN.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cloud%20NGFW%20by%20Palo%20Alto%20Networks/Data%20Connectors/CloudNgfwByPAN.json) |

[→ View full connector details](../connectors/azurecloudngfwbypaloaltonetworks.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `fluentbit_CL` | [Azure CloudNGFW By Palo Alto Networks](../connectors/azurecloudngfwbypaloaltonetworks.md) |

[← Back to Solutions Index](../solutions-index.md)
