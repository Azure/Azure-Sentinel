# Forescout eyeInspect for OT Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Forescout Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forescout.com/support](https://www.forescout.com/support) |
| **Categories** | domains |
| **First Published** | 2025-07-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Forescout eyeInspect for OT Security](../connectors/forescout-eyeinspect-for-ot-security.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ForescoutOtAlert_CL`](../tables/forescoutotalert-cl.md) | [Forescout eyeInspect for OT Security](../connectors/forescout-eyeinspect-for-ot-security.md) | Workbooks |
| [`ForescoutOtAsset_CL`](../tables/forescoutotasset-cl.md) | [Forescout eyeInspect for OT Security](../connectors/forescout-eyeinspect-for-ot-security.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [eyeInspectOTSecurityWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20eyeInspect%20for%20OT%20Security/Workbooks/eyeInspectOTSecurityWorkbook.json) | [`ForescoutOtAlert_CL`](../tables/forescoutotalert-cl.md)<br>[`ForescoutOtAsset_CL`](../tables/forescoutotasset-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------| 
| 3.0.0       | 14-07-2025                     |	Initial Solution Release                                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
