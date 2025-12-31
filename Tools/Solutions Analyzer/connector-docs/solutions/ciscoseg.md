# CiscoSEG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Cisco Secure Email Gateway via Legacy Agent](../connectors/ciscoseg.md)
- [[Deprecated] Cisco Secure Email Gateway via AMA](../connectors/ciscosegama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Cisco Secure Email Gateway via AMA](../connectors/ciscosegama.md), [[Deprecated] Cisco Secure Email Gateway via Legacy Agent](../connectors/ciscoseg.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cisco SEG - DLP policy violation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGDLPViolation.yaml) | Medium | Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Malicious attachment not blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGMaliciousAttachmentNotBlocked.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Multiple large emails sent to external recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGMultipleLargeEmails.yaml) | Medium | Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Multiple suspiciuos attachments received](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGMultipleSuspiciousEmails.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Possible outbreak](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGPossibleOutbreak.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Potential phishing link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGPotentialLinkToMalwareDownload.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Suspicious link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGSuspiciousLink.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Suspicious sender domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGSuspiciousSenderDomain.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Unexpected attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGUnexpextedAttachment.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Unexpected link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGUnclassifiedLink.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Unscannable attacment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Analytic%20Rules/CiscoSEGUnscannableAttachment.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cisco SEG - DKIM failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGFailedDKIMFailure.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - DMARK failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGFailedDMARKFailure.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Dropped incoming mails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGDroppedInMails.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Dropped outgoing mails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGDroppedOutMails.yaml) | Exfiltration | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Failed incoming TLS connections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGFailedTLSIn.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Failed outgoing TLS connections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGFailedTLSOut.yaml) | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Insecure protocol](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGInsecureProtocol.yaml) | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - SPF failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGFailedSPFFailure.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Sources of spam mails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGSpamMails.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Cisco SEG - Top users receiving spam mails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Hunting%20Queries/CiscoSEGUsersReceivedSpam.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CiscoSEG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Workbooks/CiscoSEG.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoSEGEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Parsers/CiscoSEGEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.5       | 02-12-2024                     | Added Missed Column **Parser**                                     |
| 3.0.4       | 14-11-2024                     | Removed Deprecated **Data Connector**                              |
| 3.0.3       | 08-07-2024                     | Deprecated **Data Connector**   								    |
| 3.0.2       | 03-05-2024                     | Repackaged for parser issue fix on reinstall                       |
| 3.0.1       | 30-04-2024                     | Updated the **Data Connector** to fix conectivity criteria query   |
| 3.0.0       | 28-09-2023                     | Addition of new CiscoSEG AMA **Data Connector**                 | 	                                                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
