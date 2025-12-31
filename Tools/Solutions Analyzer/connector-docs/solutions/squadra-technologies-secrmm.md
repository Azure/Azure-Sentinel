# Squadra Technologies SecRmm

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Squadra Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.squadratechnologies.com/Contact.aspx](https://www.squadratechnologies.com/Contact.aspx) |
| **Categories** | domains |
| **First Published** | 2022-05-09 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Squadra Technologies secRMM](../connectors/squadratechnologiessecrmm.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`secRMM_CL`](../tables/secrmm-cl.md) | [Squadra Technologies secRMM](../connectors/squadratechnologiessecrmm.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Removable storage ONLINE event from secRMM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm/Analytic%20Rules/Removable_Storage_ONLINE.yaml) | High | Collection | [`secRMM_CL`](../tables/secrmm-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AzureSentinelWorkbookForRemovableStorageSecurityEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Squadra%20Technologies%20SecRmm/Workbooks/AzureSentinelWorkbookForRemovableStorageSecurityEvents.json) | [`secRMM_CL`](../tables/secrmm-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 15-11-2025                     | Added **Analytical Rule** 					 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
