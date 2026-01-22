# Microsoft Defender for Cloud Apps

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md)

**Publisher:** Microsoft

By connecting with [Microsoft Defender for Cloud Apps](https://aka.ms/asi-mcas-connector-description) you will gain visibility into your cloud apps, get sophisticated analytics to identify and combat cyberthreats, and control how your data travels.



-   Identify shadow IT cloud apps on your network.

-   Control and limit access based on conditions and session context.

-   Use built-in or custom policies for data sharing and data loss prevention.

-   Identify high-risk use and get alerts for unusual user activities with Microsoft behavioral analytics and anomaly detection capabilities, including ransomware activity, impossible travel, suspicious email forwarding rules, and mass download of files.

-   Mass download of files



[Deploy now >](https://aka.ms/asi-mcas-connector-deploynow)

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Licenses:**
- Microsoft Defender for Cloud Apps

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Defender for Cloud Apps to Microsoft Sentinel**

In the Microsoft Defender for Cloud Apps portal, under Settings, select Security extensions and then SIEM and set Microsoft Sentinel as your SIEM agent. For more information, see  [Microsoft Defender for Cloud Apps](https://aka.ms/azuresentinelmcas) .

After you connect Microsoft Defender for Cloud Apps, the alerts and discovery logs are sent to this Microsoft Sentinel workspace.​
**Select Microsoft Defender for Cloud Apps Data Types**

In the Microsoft Sentinel portal, select which data types to enable:

- ☐ **Alerts**
- ☐ **Cloud Discovery Logs (Preview)**

Each data type may have specific licensing requirements. Review the information provided for each type in the portal before enabling.

> 💡 **Portal-Only Feature**: Data type selection is only available in the Microsoft Sentinel portal.

| | |
|--------------------------|---|
| **Tables Ingested** | `McasShadowItReporting` |
| | `SecurityAlert` |
| | `discoveryLogs` |
| **Connector Definition Files** | [MicrosoftCloudAppSecurity.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps/Data%20Connectors/MicrosoftCloudAppSecurity.JSON) |

[→ View full connector details](../connectors/microsoftcloudappsecurity.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `McasShadowItReporting` | [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md) |
| `SecurityAlert` | [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md) |
| `discoveryLogs` | [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
