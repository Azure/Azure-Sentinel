# VMware vCenter

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] VMware vCenter](../connectors/vmwarevcenter.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`vcenter_CL`](../tables/vcenter-cl.md) | [[Deprecated] VMware vCenter](../connectors/vmwarevcenter.md) | Analytics, Workbooks |

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
| [VMware vCenter - Root login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Analytic%20Rules/vCenterRootLogin.yaml) | High | InitialAccess, PrivilegeEscalation | [`vcenter_CL`](../tables/vcenter-cl.md) |
| [vCenter - Root impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Analytic%20Rules/vCenter-Root%20impersonation.yaml) | Medium | PrivilegeEscalation | [`vcenter_CL`](../tables/vcenter-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [vCenter](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Workbooks/vCenter.json) | [`vcenter_CL`](../tables/vcenter-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [vCenter](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Parsers/vCenter.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 13-06-2025                     | Updating **Parser** to improve data parsing logic and adjusts entity mappings.  |
| 3.0.4       | 03-12-2024                     | Removed Deprecated **Data Connector**.       |
| 3.0.3       | 18-11-2024                     | Modified **Parser** vCenter.yaml for better parsing.                 |
| 3.0.2       | 09-08-2024                     | Deprecating **Data Connectors**.                 |
| 3.0.1       | 27-05-2024                     | Updated the **Data Connector** instructions. | 
| 3.0.0       | 27-07-2023                     | Corrected the links in the solution.         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
