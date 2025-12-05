# VMWareESXi

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_VMwareESXi.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Data%20Connectors/Connector_Syslog_VMwareESXi.json) |

[→ View full connector details](../connectors/vmwareesxi.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] VMware ESXi](../connectors/vmwareesxi.md) |

[← Back to Solutions Index](../solutions-index.md)
