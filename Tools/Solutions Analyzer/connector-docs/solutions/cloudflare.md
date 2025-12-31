# Cloudflare

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cloudflare |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cloudflare.com](https://support.cloudflare.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Cloudflare](../connectors/cloudflaredataconnector.md)
- [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md) | [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](../connectors/cloudflaredefinition.md) | Analytics, Hunting |
| [`Cloudflare_CL`](../tables/cloudflare-cl.md) | [[DEPRECATED] Cloudflare](../connectors/cloudflaredataconnector.md) | Analytics, Hunting, Workbooks |

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
| [Cloudflare - Bad client IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareBadClientIp.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Client request from country in blocklist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareUnexpectedCountry.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Empty user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareEmptyUA.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Multiple error requests from single source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareMultipleErrorsSource.yaml) | Low | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Multiple user agents for single source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareMultipleUAs.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Unexpected POST requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareUnexpectedPost.yaml) | Medium | Persistence, CommandAndControl | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Unexpected URI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareUnexpectedUrl.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Unexpected client request](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareUnexpectedRequest.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - WAF Allowed threat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareWafThreatAllowed.yaml) | High | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - XSS probing pattern in request](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Analytic%20Rules/CloudflareXSSProbingPattern.yaml) | Medium | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cloudflare - Client TLS errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareClientTlsErrors.yaml) | InitialAccess, Impact | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Client errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareClientErrors.yaml) | InitialAccess, Impact | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Files requested](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareFilesRequested.yaml) | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Rare user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareRareUAs.yaml) | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Server TLS errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareServerTlsErrors.yaml) | InitialAccess, Impact | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Server errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareServerErrors.yaml) | InitialAccess, Impact | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Top Network rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareTopNetworkRules.yaml) | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Top WAF rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareTopWafRules.yaml) | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Unexpected countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareUnexpectedCountries.yaml) | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |
| [Cloudflare - Unexpected edge response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Hunting%20Queries/CloudflareUnexpectedEdgeResponse.yaml) | InitialAccess | [`CloudflareV2_CL`](../tables/cloudflarev2-cl.md)<br>[`Cloudflare_CL`](../tables/cloudflare-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Cloudflare](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Workbooks/Cloudflare.json) | [`Cloudflare_CL`](../tables/cloudflare-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Cloudflare](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Parsers/Cloudflare.yaml) | - | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2      | 05-09-2024                    | Updated the python runtime version to 3.11                                                |
| 3.0.1      | 01-08-2023                    | Updated logic in **Data Connector** to handle broken events.                              |
| 3.0.0      | 24-07-2023                    | Updated logic in **Hunting Query** (Cloudflare - Client errors,Cloudflare - Server errors)|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
