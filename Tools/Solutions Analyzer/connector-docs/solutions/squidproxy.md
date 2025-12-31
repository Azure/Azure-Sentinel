# SquidProxy

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Squid Proxy](../connectors/squidproxy.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | [[Deprecated] Squid Proxy](../connectors/squidproxy.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SquidProxy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy/Parsers/SquidProxy.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.2       | 16-05-2025                     | Optimized **Parser** for improved performance and parsing accuracy                       |
| 3.0.1       | 16-12-2024                     | Removed Deprecated **Data Connector**                       |
| 3.0.0       | 12-08-2024                     | Deprecating **Data Connector**                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
