# Acronis Cyber Protect Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Acronis International GmbH |
| **Support Tier** | Partner |
| **Support Link** | [https://www.acronis.com/en/support](https://www.acronis.com/en/support) |
| **Categories** | domains,verticals |
| **First Published** | 2025-10-28 |
| **Last Updated** | 2025-10-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Analytics, Hunting |

## Content Items

This solution includes **17 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 13 |
| Analytic Rules | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Acronis - Login from Abnormal IP - Low Occurrence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisLoginFromAbnormalIPLowOccurrence.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Multiple Endpoints Accessing Malicious URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisMultipleEndpointsAccessingMaliciousURLs.yaml) | Medium | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Multiple Endpoints Infected by Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisMultipleEndpointsInfectedByRansomware.yaml) | High | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Multiple Inboxes with Malicious Content Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisMultipleInboxesWithMaliciousContentDetected.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Acronis - ASZ defence: Unauthorized operation is detected and blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisUnauthorizedOperationIsDetected.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Agent failed updating more than twice in a day](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisAgentFailedUpdatingMoreThanTwiceInADay.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Agents offline for 2 days or more](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisAgentsOfflineFor2DaysOrMore.yaml) | DefenseEvasion | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Audit Log](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisAuditLog.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Cloud Connection Errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisCloudConnectionErrors.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Endpoints Accessing Malicious URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsAccessingMaliciousURLs.yaml) | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Endpoints Infected by Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsInfectedByRansomware.yaml) | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Endpoints with Backup issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsWithBackupIssues.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Endpoints with EDR Incidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsWithEDRIncidents.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Endpoints with high failed login attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsWithHighFailedLoginAttempts.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Inboxes with Malicious Content](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisInboxesWithMaliciousContentDetected.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Login from Abnormal IP - Low Occurrence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisLoginFromAbnormalIPLowOccurrence.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Acronis - Protection Service Errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisProtectionServiceErrors.yaml) | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 11-11-2025                     | Initial Solution Release. <br> The **publisherId** has been Updated.|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
