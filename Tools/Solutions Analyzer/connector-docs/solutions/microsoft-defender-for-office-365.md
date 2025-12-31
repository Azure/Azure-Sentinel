# Microsoft Defender for Office 365

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Defender for Office 365 (Preview)](../connectors/officeatp.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`EmailAttachmentInfo`](../tables/emailattachmentinfo.md) | - | Workbooks |
| [`EmailEvents`](../tables/emailevents.md) | - | Workbooks |
| [`EmailUrlInfo`](../tables/emailurlinfo.md) | - | Workbooks |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft Defender for Office 365 (Preview)](../connectors/officeatp.md) | - |

## Content Items

This solution includes **21 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 20 |
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MicrosoftDefenderForOffice365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Workbooks/MicrosoftDefenderForOffice365.json) | [`EmailAttachmentInfo`](../tables/emailattachmentinfo.md)<br>[`EmailEvents`](../tables/emailevents.md)<br>[`EmailUrlInfo`](../tables/emailurlinfo.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [O365 - Block Malware file extensions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/O365DefenderPlaybooks/o365-BlockMalwareFileExtension/azuredeploy.json) | This Playbook Provides the automation on blocking the suspicious/malicious file attachment on mails | - |
| [O365 - Block Sender Entity Trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/O365DefenderPlaybooks/o365-BlockSender-EntityTrigger/azuredeploy.json) | This Playbook Provides the automation on blocking the suspicious/malicious sender | - |
| [O365 - Block Spam Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/O365DefenderPlaybooks/o365-BlockSpamDomain/azuredeploy.json) | This Playbook Provides the automation on blocking the suspicious/malicious attacker Domains | - |
| [O365 - Block Suspicious Sender](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/O365DefenderPlaybooks/o365-BlockSender/azuredeploy.json) | This Playbook Provides the automation on blocking the suspicious/malicious senders | - |
| [O365 - Delete All Malicious Inbox Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/O365DefenderPlaybooks/o365-DeleteMaliciousInboxRule/azuredeploy.json) | This Playbook provides the automation on deleting all the suspicious/malicious Inbox Rules from Prov... | - |
| [O365_Defender_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/azuredeploy.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/BlockMalwareFileExtension/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/ConnectExchangeOnline/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/CreateAllowBlockList/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/CreateSpamPolicy/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/CreateSpamRule/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/DisconnectExchangeOnline/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/GetInboxRule/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/ListMalwarePolicy/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/ListSpamPolicy/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/RemoveAllowBlockListItems/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/RemoveInboxRule/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/TenantAllowBlockList/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/UpdateAllowBlockList/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Playbooks/CustomConnector/O365_Defender_FunctionAppConnector/host.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.3       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |
| 3.0.2       | 24-04-2024                     | Updated link for **Custom Connector** redirection in playbooks           |
| 3.0.1       | 29-09-2023                     | 1 new **Playbook** added to the solution                                 |
| 3.0.0       | 11-07-2023                     | 4 new **Playbooks** added to the solution                                |
|             |                                | 1 **Custom Connector** added as a pre-requisite for playbooks deployment |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
