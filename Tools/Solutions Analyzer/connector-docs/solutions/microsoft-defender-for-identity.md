# Microsoft Defender For Identity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-04-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20For%20Identity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20For%20Identity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Defender for Identity](../connectors/azureadvancedthreatprotection.md)

**Publisher:** Microsoft

Connect Microsoft Defender for Identity to gain visibility into the events and user analytics. Microsoft Defender for Identity identifies, detects, and helps you investigate advanced threats, compromised identities, and malicious insider actions directed at your organization. Microsoft Defender for Identity enables SecOp analysts and security professionals struggling to detect advanced attacks in hybrid environments to:



-   Monitor users, entity behavior, and activities with learning-based analytics​

-   Protect user identities and credentials stored in Active Directory

-   Identify and investigate suspicious user activities and advanced attacks throughout the kill chain

-   Provide clear incident information on a simple timeline for fast triage



[Try now >](https://aka.ms/AtpTryNow)



[Deploy now >](https://aka.ms/AzureATP_Deploy)



For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2220069&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Licenses:**
- Microsoft Defender for Identity

**Tenant Permissions:**
Requires SecurityAdmin, GlobalAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Defender for Identity to Microsoft Sentinel**

If your tenant is running [Microsoft Defender for Identity](https://aka.ms/Sentinel/MDI/Preview)  in Microsoft Defender for Cloud Apps, connect here to stream your Microsoft Defender for Identity alerts into Microsoft Sentinel

> In order to integrate with Microsoft Defender for Identity alerts, use  **global administrator**, or  **security administrator**  permission.
- Connect Microsoft Defender for Identity

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [MicrosoftDefenderforIdentity.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20For%20Identity/Data%20Connectors/MicrosoftDefenderforIdentity.JSON) |

[→ View full connector details](../connectors/azureadvancedthreatprotection.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Microsoft Defender for Identity](../connectors/azureadvancedthreatprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
