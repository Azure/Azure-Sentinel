# archTIS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | archTIS |
| **Support Tier** | Partner |
| **Support Link** | [https://www.archtis.com/nc-protect-support/](https://www.archtis.com/nc-protect-support/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [NC Protect](../connectors/nucleuscyberncprotect.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`NCProtectUAL_CL`](../tables/ncprotectual-cl.md) | [NC Protect](../connectors/nucleuscyberncprotect.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NucleusCyber_NCProtect_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS/Workbooks/NucleusCyber_NCProtect_Workbook.json) | [`NCProtectUAL_CL`](../tables/ncprotectual-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
