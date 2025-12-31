# HYAS Protect

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | HYAS |
| **Support Tier** | Partner |
| **Support Link** | [https://www.hyas.com/contact](https://www.hyas.com/contact) |
| **Categories** | domains |
| **First Published** | 2023-09-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HYAS%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HYAS%20Protect) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [HYAS Protect](../connectors/hyasprotect.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`HYASProtectDnsSecurityLogs_CL`](../tables/hyasprotectdnssecuritylogs-cl.md) | [HYAS Protect](../connectors/hyasprotect.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [HYASProtectDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HYAS%20Protect/Parsers/HYASProtectDNS.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 04-06-2024                     | Updated **Parser** and **Data connector**  |
| 3.0.1       | 23-04-2024                     | Updated Solution version for Partner Center policy regulations|
| 3.0.0       | 22-09-2023                     | Initial Solution Release                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
