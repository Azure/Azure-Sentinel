# Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-08-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Fortinet via Legacy Agent](../connectors/fortinet.md)

**Publisher:** Fortinet

The Fortinet firewall connector allows you to easily connect your Fortinet logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Fortinet-FortiGate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/Fortinet-FortiGate.json) |

[→ View full connector details](../connectors/fortinet.md)

### [[Deprecated] Fortinet via AMA](../connectors/fortinetama.md)

**Publisher:** Fortinet

The Fortinet firewall connector allows you to easily connect your Fortinet logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_Fortinet-FortiGateAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_Fortinet-FortiGateAma.json) |

[→ View full connector details](../connectors/fortinetama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Fortinet via AMA](../connectors/fortinetama.md), [[Deprecated] Fortinet via Legacy Agent](../connectors/fortinet.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                      |
|-------------|--------------------------------|-----------------------------------------------------------------------------------------|
| 3.0.9       | 02-09-2025                     |Update Fortinetfortigate **Playbook**  fix                                               |
| 3.0.8       | 26-02-2025                     |**Playbook** functionApp code change                                                     |
| 3.0.7       | 11-11-2024                     |Removed Deprecated data connectors                                                       |
| 3.0.6       | 22-08-2024                     |Deprecated data connectors                                                    			 |
| 3.0.5       | 05-04-2024                     |Workbook queries are optimized to fix timeout issues  									 |
| 3.0.4       | 29-01-2024                     |Classic app insights to Log analytics                                                    |
|             |                                |Addition of new Fortinet FortiGate AMA Data Connector                                    | 
| 3.0.3       | 07-11-2023                     |Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.  |
| 3.0.2       | 10-08-2023                     |Added the missing userAssignedIdentities field for UserAssigned type in the **Playbooks**|
| 3.0.1       | 21-07-2023                     |Updated the description in the solution                                                  |
| 3.0.0       | 11-07-2023                     |Updated the title, logo and the description in the solution                              |

[← Back to Solutions Index](../solutions-index.md)
