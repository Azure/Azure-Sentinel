# Azure DDoS Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure DDoS Protection](../connectors/ddos.md)

**Publisher:** Microsoft

Connect to Azure DDoS Protection Standard logs via Public IP Address Diagnostic Logs. In addition to the core DDoS protection in the platform, Azure DDoS Protection Standard provides advanced DDoS mitigation capabilities against network attacks. It's automatically tuned to protect your specific Azure resources. Protection is simple to enable during the creation of new virtual networks. It can also be done after creation and requires no application or resource changes. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219760&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [DDOS.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Data%20Connectors/DDOS.JSON) |

[→ View full connector details](../connectors/ddos.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure DDoS Protection](../connectors/ddos.md) |

[← Back to Solutions Index](../solutions-index.md)
