# RSA SecurID

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] RSA® SecurID (Authentication Manager)](../connectors/rsasecuridam.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] RSA® SecurID (Authentication Manager)](../connectors/rsasecuridam.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [RSASecurIDAMEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID/Parsers/RSASecurIDAMEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.0.1       | 26-12-2024                     | Removed Deprecated **Data connector**                                          |
| 3.0.0       | 01-08-2024                     |Update **Parser** as part of Syslog migration                                   |
|             |                                |Deprecating data connectors                                                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
