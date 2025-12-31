# Trend Micro Cloud App Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Trend Micro Cloud App Security](../connectors/trendmicrocas.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) | [Trend Micro Cloud App Security](../connectors/trendmicrocas.md) | Analytics, Hunting, Workbooks |

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
| [Trend Micro CAS - DLP violation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASDLPViolation.yaml) | High | Exfiltration | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Infected user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASVAInfectedUser.yaml) | High | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Multiple infected users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASVAOutbreak.yaml) | High | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Possible phishing mail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASPossiblePhishingMail.yaml) | Medium | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Ransomware infection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASRansomwareOnHost.yaml) | High | Impact | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Ransomware outbreak](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASRansomwareOutbreak.yaml) | High | Impact | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Suspicious filename](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASSuspiciousFilename.yaml) | Medium | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Threat detected and not blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASThreatNotBlocked.yaml) | High | DefenseEvasion | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Unexpected file on file share](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASUnexpectedFileOnFileShare.yaml) | Medium | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Unexpected file via mail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Analytic%20Rules/TrendMicroCASUnexpectedFileInMail.yaml) | Medium | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Trend Micro CAS - DLP violations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASUserDLPViolations.yaml) | Exfiltration | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Files received via email services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASTopFilesRecievedViaEmail.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Files stored on cloud fileshare services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASFilesOnShares.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Infected files received via email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASInfectedFilesInEmails.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Ransomware threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASRansomwareThreats.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Rare files received via email services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASRareFilesRecievedViaEmail.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Risky users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASRiskyUsers.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Security risk scan threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASScanDiscoveredThreats.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Suspicious files on sharepoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASSuspiciousFilesSharepoint.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |
| [Trend Micro CAS - Virtual Analyzer threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Hunting%20Queries/TrendMicroCASVAThreats.yaml) | InitialAccess | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TrendMicroCAS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Workbooks/TrendMicroCAS.json) | [`TrendMicroCAS_CL`](../tables/trendmicrocas-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TrendMicroCAS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Cloud%20App%20Security/Parsers/TrendMicroCAS.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
