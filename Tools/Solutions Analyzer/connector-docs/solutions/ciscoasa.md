# CiscoASA

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Cisco ASA via Legacy Agent](../connectors/ciscoasa.md)

**Publisher:** Cisco

The Cisco ASA firewall connector allows you to easily connect your Cisco ASA logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [CiscoASA.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/CiscoASA.JSON) |

[→ View full connector details](../connectors/ciscoasa.md)

### [Cisco ASA/FTD via AMA](../connectors/ciscoasaama.md)

**Publisher:** Microsoft

The Cisco ASA firewall connector allows you to easily connect your Cisco ASA logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CiscoAsaAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/template_CiscoAsaAma.JSON) |

[→ View full connector details](../connectors/ciscoasaama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Cisco ASA via Legacy Agent](../connectors/ciscoasa.md), [Cisco ASA/FTD via AMA](../connectors/ciscoasaama.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.7       | 01-09-2025                     | Updates to the `template_CiscoAsaAma.json` file to reflect the general availability of the Cisco ASA/FTD via AMA connector  					  				  |
| 3.0.6       | 10-07-2025                     | Preview tag removed from Connector title  					  				  |
| 3.0.5       | 25-04-2025                     | Removed Legacy **Data Connector**   					  					  |
| 3.0.4       | 22-05-2024                     | Updated connectivity criteria for **Data Connector**   					  |
| 3.0.3       | 14-03-2024                     | Change the connectivity criteria to use the resource graph and not LA data   |
| 3.0.2       | 07-03-2024                     | New AMA based connector is now in public preview							  |
| 3.0.1       | 31-01-2023                     | Added new **Data Connector** Cisco ASA/FTD via AMA (Preview) to the solution |

[← Back to Solutions Index](../solutions-index.md)
