# VMWareESXi

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] VMware ESXi](../connectors/vmwareesxi.md)

**Publisher:** VMWare

The [VMware ESXi](https://www.vmware.com/products/esxi-and-esx.html) connector allows you to easily connect your VMWare ESXi logs with Microsoft Sentinel This gives you more insight into your organization's ESXi servers and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_VMwareESXi.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Data%20Connectors/Connector_Syslog_VMwareESXi.json) |

[→ View full connector details](../connectors/vmwareesxi.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] VMware ESXi](../connectors/vmwareesxi.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.5       | 03-11-2025                     | Added new **Analytic Rule** (VMware ESXi - Root change password) and (VMware ESXi - Multiple Failed SSH Login)      |
| 3.0.4       | 09-10-2025                     | Added new **Analytic Rule** (VMware ESXi - SSH Enable on ESXi Host)    |
| 3.0.3       | 02-12-2024                     | Removed Deprecated **Data connectors**                                 |
| 3.0.2       | 01-08-2024                     | Update **Parser** as part of Syslog migration                          |
|             |                                | Deprecating data connectors                                            |
| 3.0.1       | 30-04-2024                     | Repackaged for parser name issue                                       |
| 3.0.0       | 15-04-2024                     | Updated **Parser** VMwareESXi.yaml to automatic update applicable logs |

[← Back to Solutions Index](../solutions-index.md)
