# ESETPROTECT

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ESET Netherlands |
| **Support Tier** | Partner |
| **Support Link** | [https://techcenter.eset.nl/en/](https://techcenter.eset.nl/en/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESETPROTECT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESETPROTECT) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] ESET PROTECT](../connectors/esetprotect.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] ESET PROTECT](../connectors/esetprotect.md) | Analytics, Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Threats detected by ESET](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESETPROTECT/Analytic%20Rules/ESETThreatDetected.yaml) | Low | Execution | [`Syslog`](../tables/syslog.md) |
| [Website blocked by ESET](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESETPROTECT/Analytic%20Rules/ESETWebsiteBlocked.yaml) | Low | Exfiltration, CommandAndControl, InitialAccess | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ESETPROTECT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESETPROTECT/Workbooks/ESETPROTECT.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ESETPROTECT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESETPROTECT/Parsers/ESETPROTECT.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 19-07-2024                     | Deprecating data connectors                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
