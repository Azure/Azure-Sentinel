# AI Analyst Darktrace

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Darktrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.darktrace.com/en/contact/](https://www.darktrace.com/en/contact/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] AI Analyst Darktrace via Legacy Agent](../connectors/darktrace.md)
- [[Deprecated] AI Analyst Darktrace via AMA](../connectors/darktraceama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] AI Analyst Darktrace via AMA](../connectors/darktraceama.md), [[Deprecated] AI Analyst Darktrace via Legacy Agent](../connectors/darktrace.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AIA-Darktrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace/Workbooks/AIA-Darktrace.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 18-09-2023                     |	Addition of new AI Analyst Darktrace AMA **Data Connector**     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
