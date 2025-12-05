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
