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

This solution provides **1 data connector(s)**.

### [Microsoft Defender for Office 365 (Preview)](../connectors/officeatp.md)

**Publisher:** Microsoft

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

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [template_OfficeATP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Data%20Connectors/template_OfficeATP.json) |

[→ View full connector details](../connectors/officeatp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Microsoft Defender for Office 365 (Preview)](../connectors/officeatp.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.3       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |
| 3.0.2       | 24-04-2024                     | Updated link for **Custom Connector** redirection in playbooks           |
| 3.0.1       | 29-09-2023                     | 1 new **Playbook** added to the solution                                 |
| 3.0.0       | 11-07-2023                     | 4 new **Playbooks** added to the solution                                |
|             |                                | 1 **Custom Connector** added as a pre-requisite for playbooks deployment |

[← Back to Solutions Index](../solutions-index.md)
