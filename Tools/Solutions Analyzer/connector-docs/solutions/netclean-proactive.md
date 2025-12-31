# NetClean ProActive

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | NetClean |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netclean.com/contact](https://www.netclean.com/contact) |
| **Categories** | domains |
| **First Published** | 2022-06-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Netclean ProActive Incidents](../connectors/netclean-proactive-incidents.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Netclean_Incidents_CL`](../tables/netclean-incidents-cl.md) | [Netclean ProActive Incidents](../connectors/netclean-proactive-incidents.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [NetClean ProActive Incidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive/Analytic%20Rules/NetClean_Sentinel_analytic_rule.yaml) | High | Discovery | [`Netclean_Incidents_CL`](../tables/netclean-incidents-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NetCleanProActiveWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive/Workbooks/NetCleanProActiveWorkbook.json) | [`Netclean_Incidents_CL`](../tables/netclean-incidents-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 30-01-2025                     | Updated **Analytic Rules**, **Workbook** columns due to change in **Data Connector**  |
| 3.0.1       | 27-07-2023                     | Updated solution to remove unwanted spaces from variables.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
