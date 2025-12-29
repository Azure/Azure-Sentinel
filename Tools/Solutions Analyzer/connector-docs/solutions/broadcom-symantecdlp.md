# Broadcom SymantecDLP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Broadcom Symantec DLP via Legacy Agent](../connectors/broadcomsymantecdlp.md)

**Publisher:** Broadcom

The [Broadcom Symantec Data Loss Prevention (DLP)](https://www.broadcom.com/products/cyber-security/information-protection/data-loss-prevention) connector allows you to easily connect your Symantec DLP with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s information, where it travels, and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_Syslog_SymantecDLP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Data%20Connectors/Connector_Syslog_SymantecDLP.json) |

[→ View full connector details](../connectors/broadcomsymantecdlp.md)

### [[Deprecated] Broadcom Symantec DLP via AMA](../connectors/broadcomsymantecdlpama.md)

**Publisher:** Broadcom

The [Broadcom Symantec Data Loss Prevention (DLP)](https://www.broadcom.com/products/cyber-security/information-protection/data-loss-prevention) connector allows you to easily connect your Symantec DLP with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s information, where it travels, and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_SymantecDLPAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Data%20Connectors/template_SymantecDLPAMA.json) |

[→ View full connector details](../connectors/broadcomsymantecdlpama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Broadcom Symantec DLP via AMA](../connectors/broadcomsymantecdlpama.md), [[Deprecated] Broadcom Symantec DLP via Legacy Agent](../connectors/broadcomsymantecdlp.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 27-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.2       | 08-07-2024                     | Deprecated **Data Connector**   								    |
| 3.0.1       | 01-09-2023                     | Addition of new Broadcom SymantecDLP AMA **Data Connector**        |
| 3.0.0       | 27-07-2023                     | Corrected the links in the solution.                               |

[← Back to Solutions Index](../solutions-index.md)
