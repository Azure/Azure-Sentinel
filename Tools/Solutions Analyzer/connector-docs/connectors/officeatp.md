# Microsoft Defender for Office 365 (Preview)

| | |
|----------|-------|
| **Connector ID** | `OfficeATP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SecurityAlert`](../tables-index.md#securityalert) |
| **Used in Solutions** | [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md) |
| **Connector Definition Files** | [template_OfficeATP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Data%20Connectors/template_OfficeATP.json) |

Microsoft Defender for Office 365 safeguards your organization against malicious threats posed by email messages, links (URLs) and collaboration tools. By ingesting Microsoft Defender for Office 365 alerts into Microsoft Sentinel, you can incorporate information about email- and URL-based threats into your broader risk analysis and build response scenarios accordingly.

 

The following types of alerts will be imported:



-   A potentially malicious URL click was detected 

-   Email messages containing malware removed after delivery

-   Email messages containing phish URLs removed after delivery

-   Email reported by user as malware or phish 

-   Suspicious email sending patterns detected 

-   User restricted from sending email 



These alerts can be seen by Office customers in the ** Office Security and Compliance Center**.



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219942&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
