# Onapsis Platform

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Onapsis |
| **Support Tier** | Partner |
| **Support Link** | [https://onapsis.com/company/contact-us](https://onapsis.com/company/contact-us) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Onapsis Platform](../connectors/onapsisplatform.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Onapsis Platform](../connectors/onapsisplatform.md) | Workbooks |
| [`incident_lookup`](../tables/incident-lookup.md) | - | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [OnapsisAlarmsOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform/Workbooks/OnapsisAlarmsOverview.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`incident_lookup`](../tables/incident-lookup.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OnapsisLookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform/Parsers/OnapsisLookup.yaml) | - | - |

## Release Notes

| **Version**   | **Date Modified**              | **Change History**                      |
|---------------|--------------------------------|-----------------------------------------|
| 3.0.0         | 28-06-2024                     | Deprecating data connectors  |
| 2.0.1         | 01-02-2023                     | Updated CreateUi file |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
