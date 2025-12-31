# vArmour Application Controller

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | vArmour Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varmour.com/contact-us/](https://www.varmour.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] vArmour Application Controller via Legacy Agent](../connectors/varmourac.md)
- [[Deprecated] vArmour Application Controller via AMA](../connectors/varmouracama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] vArmour Application Controller via AMA](../connectors/varmouracama.md), [[Deprecated] vArmour Application Controller via Legacy Agent](../connectors/varmourac.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [vArmour AppController - SMB Realm Traversal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Analytic%20Rules/vArmourApplicationControllerSMBRealmTraversal.yaml) | Medium | Discovery, LateralMovement | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [vArmour_AppContoller_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Workbooks/vArmour_AppContoller_Workbook.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.1       | 27-06-2024                     | Deprecating data connectors            |
| 3.0.0       | 04-09-2023                     | Addition of new vArmour Application Controller AMA **Data Connector** | 	                                                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
