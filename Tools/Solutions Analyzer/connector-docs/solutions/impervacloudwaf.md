# ImpervaCloudWAF

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Imperva Cloud WAF](../connectors/impervacloudwaflogsccfdefinition.md)
- [Imperva Cloud WAF](../connectors/impervawafcloudapi.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md) | [Imperva Cloud WAF](../connectors/impervacloudwaflogsccfdefinition.md), [Imperva Cloud WAF](../connectors/impervawafcloudapi.md) | Analytics, Hunting, Workbooks |
| [`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) | [Imperva Cloud WAF](../connectors/impervawafcloudapi.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Imperva - Abnormal protocol usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaAbnormalProtocolUsage.yaml) | Medium | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Critical severity event not blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaAttackNotBlocked.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Forbidden HTTP request method in request](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaForbiddenMethod.yaml) | Medium | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Malicious Client](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaMaliciousClient.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Malicious user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaMaliciousUA.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Multiple user agents from same source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaMultipleUAsSource.yaml) | Medium | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Possible command injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaCommandInUri.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Request from unexpected IP address to admin panel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaAdminPanelUncommonIp.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Request from unexpected countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaForbiddenCountry.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Request to unexpected destination port](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Analytic%20Rules/ImpervaSuspiciousDstPort.yaml) | High | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Imperva - Applications with insecure web protocol version](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaInsecureWebProtocolVersion.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Non HTTP/HTTPs applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaNonWebApplication.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Rare applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRareApplications.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Rare client applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRareClientApplications.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Rare destination ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRareDstPorts.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Top applications with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaTopApplicationsErrors.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Top destinations with blocked requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaDestinationBlocked.yaml) | InitialAccess, Impact | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Top sources with blocked requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaSourceBlocked.yaml) | InitialAccess, Impact | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - Top sources with error requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaTopSourcesErrors.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |
| [Imperva - request from known bots](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Hunting%20Queries/ImpervaRequestsFromBots.yaml) | InitialAccess | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Imperva WAF Cloud Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Workbooks/Imperva%20WAF%20Cloud%20Overview.json) | [`ImpervaWAFCloudV2_CL`](../tables/impervawafcloudv2-cl.md)<br>[`ImpervaWAFCloud_CL`](../tables/impervawafcloud-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ImpervaWAFCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Parsers/ImpervaWAFCloud.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                               |
|-------------|--------------------------------|------------------------------------------------- |  
| 3.0.2       | 06-06-2025                     |  Migrated the **Function app** connector to **CCF** Data connector and updated **Parser**     |
| 3.0.1       | 07-11-2024                     |  Added existing ***Parser* into the solution     | 
| 3.0.0       | 22-08-2024                     |  Updated the python runtime version to **3.11**  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
