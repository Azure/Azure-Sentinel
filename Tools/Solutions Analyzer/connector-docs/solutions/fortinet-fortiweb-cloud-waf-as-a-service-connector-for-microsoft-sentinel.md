# Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Fortinet FortiWeb Web Application Firewall via Legacy Agent](../connectors/fortinetfortiweb.md)

**Publisher:** Microsoft

The [fortiweb](https://www.fortinet.com/products/web-application-firewall/fortiweb) data connector provides the capability to ingest Threat Analytics and events into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Fortiweb.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/Fortiweb.json) |

[→ View full connector details](../connectors/fortinetfortiweb.md)

### [Fortinet FortiWeb Web Application Firewall via AMA](../connectors/fortinetfortiwebama.md)

**Publisher:** Microsoft

The [fortiweb](https://www.fortinet.com/products/web-application-firewall/fortiweb) data connector provides the capability to ingest Threat Analytics and events into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_FortiwebAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_FortiwebAma.json) |

[→ View full connector details](../connectors/fortinetfortiwebama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Fortinet FortiWeb Web Application Firewall via AMA](../connectors/fortinetfortiwebama.md), [[Deprecated] Fortinet FortiWeb Web Application Firewall via Legacy Agent](../connectors/fortinetfortiweb.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                | 
|-------------|--------------------------------|-------------------------------------------------------------------|
| 3.0.3       | 10-12-2024                     | Removed Deprecated **Data Connectors**                            |
| 3.0.2       | 30-04-2024                     | Repackaged for parser issue fix on reinstall                      |
| 3.0.1       | 26-02-2024                     |Addition of new Fortinet FortiWeb Cloud WAF AMA **Data Connector** |
| 3.0.0       | 11-07-2023                     |Updated the title and the description of the solution              |

[← Back to Solutions Index](../solutions-index.md)
