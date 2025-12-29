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

This solution provides **1 data connector(s)**.

### [[Deprecated] VMware vCenter](../connectors/vmwarevcenter.md)

**Publisher:** VMware

The [vCenter](https://www.vmware.com/in/products/vcenter-server.html) connector allows you to easily connect your vCenter server logs with Microsoft Sentinel. This gives you more insight into your organization's data centers and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `vcenter_CL` |
| **Connector Definition Files** | [Connector_Syslog_vcenter.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Data%20Connectors/Connector_Syslog_vcenter.json) |

[→ View full connector details](../connectors/vmwarevcenter.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `vcenter_CL` | [[Deprecated] VMware vCenter](../connectors/vmwarevcenter.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 13-06-2025                     | Updating **Parser** to improve data parsing logic and adjusts entity mappings.  |
| 3.0.4       | 03-12-2024                     | Removed Deprecated **Data Connector**.       |
| 3.0.3       | 18-11-2024                     | Modified **Parser** vCenter.yaml for better parsing.                 |
| 3.0.2       | 09-08-2024                     | Deprecating **Data Connectors**.                 |
| 3.0.1       | 27-05-2024                     | Updated the **Data Connector** instructions. | 
| 3.0.0       | 27-07-2023                     | Corrected the links in the solution.         |

[← Back to Solutions Index](../solutions-index.md)
