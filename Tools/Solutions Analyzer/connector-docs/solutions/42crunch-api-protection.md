# 42Crunch API Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | 42Crunch API Protection |
| **Support Tier** | Partner |
| **Support Link** | [https://42crunch.com/](https://42crunch.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [API Protection](../connectors/42crunchapiprotection.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) | [API Protection](../connectors/42crunchapiprotection.md) | Analytics, Workbooks |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [API - API Scraping](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIAPIScaping.yaml) | High | Reconnaissance, Collection | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Account Takeover](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIAccountTakeover.yaml) | High | CredentialAccess, Discovery | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Anomaly Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIAnomalyDetection.yaml) | Low | Reconnaissance | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - BOLA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIBOLA.yaml) | Medium | Exfiltration | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Invalid host access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIInvalidHostAccess.yaml) | Low | Reconnaissance | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - JWT validation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIJWTValidation.yaml) | Low | InitialAccess, CredentialAccess | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Kiterunner detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIKiterunnerDetection.yaml) | Medium | Reconnaissance, Discovery | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Password Cracking](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIPasswordCracking.yaml) | High | CredentialAccess | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Rate limiting](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIFirstTimeAccess.yaml) | Low | Discovery, InitialAccess | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Rate limiting](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APIRateLimiting.yaml) | Medium | Impact | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |
| [API - Suspicious Login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Analytic%20Rules/APISuspiciousLogin.yaml) | High | CredentialAccess, InitialAccess | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [42CrunchAPIProtectionWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Workbooks/42CrunchAPIProtectionWorkbook.json) | [`apifirewall_log_1_CL`](../tables/apifirewall-log-1-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 15-07-2024                     |	Missing Tactics and Techniques added     						|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
