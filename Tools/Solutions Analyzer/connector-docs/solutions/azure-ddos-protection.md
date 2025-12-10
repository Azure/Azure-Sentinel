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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Azure DDoS protection plan**: A configured Azure DDoS Standard protection plan [read more about Azure DDoS protection plans](https://docs.microsoft.com/azure/virtual-network/manage-ddos-protection#create-a-ddos-protection-plan).
- **Enabled Azure DDoS for virtual network**: A configured virtual network with Azure DDoS Standard enabled [read more about configuring virtual network with Azure DDoS](https://docs.microsoft.com/azure/virtual-network/manage-ddos-protection#enable-ddos-for-an-existing-virtual-network).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Azure DDoS Protection to Microsoft Sentinel**

Enable Diagnostic Logs on All Public IP Addresses.
- **Open Azure Monitoring**

**2. Inside your Diagnostics settings portal, select your Public IP Address resource:**

Inside your Public IP Address resource:
    
1.  Select **+ Add diagnostic setting.​**
2.  In the **Diagnostic setting** blade:
  -   Type a **Name**, within the **Diagnostics settings** name field.
  -   Select **Send to Log Analytics**.
  -   Choose the log destination workspace.
  -   Select the categories that you want to analyze (recommended: DDoSProtectionNotifications, DDoSMitigationFlowLogs, DDoSMitigationReports)
  -   Click **Save**.

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
