# Illumio Insight

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Illumio |
| **Support Tier** | Partner |
| **Support Link** | [https://www.illumio.com/support/support](https://www.illumio.com/support/support) |
| **Categories** | domains |
| **First Published** | 2025-08-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Insight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Insight) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Illumio Insights](../connectors/illumioinsightsdefinition.md)
- [Illumio Insights Summary](../connectors/illumioinsightssummaryccp.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`IllumioInsightsSummary_CL`](../tables/illumioinsightssummary-cl.md) | [Illumio Insights Summary](../connectors/illumioinsightssummaryccp.md) | - |
| [`IllumioInsights_CL`](../tables/illumioinsights-cl.md) | [Illumio Insights](../connectors/illumioinsightsdefinition.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                  |
|-------------|--------------------------------|-----------------------------------------------------|
|3.3.2      | 29-09-2025                 | Dsecription , Instruction changes for **CCF Data Connector** , changing ps script to change desriptions in UiDefnition
| 3.3.1       | 12-09-2025                     | Adding iIlumio InsightsSummary **CCF Data Connector** to Illumio Insights Solution, changing URL of Illumio Resources to `gw.console.illum.io` |
| 3.0.0       | 10-08-2025                     | Corrected the links in the solution.  	             |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
