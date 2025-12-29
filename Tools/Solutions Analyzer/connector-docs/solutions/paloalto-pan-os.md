# PaloAlto-PAN-OS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-08-09 |
| **Last Updated** | 2021-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md)

**Publisher:** Palo Alto Networks

The Palo Alto Networks firewall connector allows you to easily connect your Palo Alto Networks logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [PaloAltoNetworks.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Data%20Connectors/PaloAltoNetworks.json) |

[→ View full connector details](../connectors/paloaltonetworks.md)

### [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md)

**Publisher:** Palo Alto Networks

The Palo Alto Networks firewall connector allows you to easily connect your Palo Alto Networks logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PaloAltoNetworksAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Data%20Connectors/template_PaloAltoNetworksAMA.json) |

[→ View full connector details](../connectors/paloaltonetworksama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md), [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.10      | 13-11-2025                     |   Adding New Detection Rule for Nmap Top 100 Port Scan             |
| 3.0.9       | 06-01-2025                     |   Removing Custom Entity mappings from **Analytic Rule**           |
| 3.0.8       | 15-11-2024                     |   Corrected **Data Connector** count in CreateUiDefinition         |
| 3.0.7 	  | 11-11-2024 					   |   Removed Deprecated **Data Connector**                            |
|             |                                |   Updated **Analytic Rule** for entity mappings                    |
| 3.0.6 	  | 12-07-2024 					   |   Deprecated **Data Connector** 									|
| 3.0.5       | 30-04-2024                     |   Updated the **Data Connector** to fix conectivity criteria query |
| 3.0.4       | 16-04-2024                     |   Fixed existing rule for sites with private IP addresses other than 10/8 |
| 3.0.3       | 11-04-2024                     |   Enhanced the existing **Workbook** as per requirement            |
| 3.0.2       | 12-02-2024                     |   Addition of new PaloAlto-PAN-OS AMA **Data Connector**           |
| 3.0.1       | 22-01-2024                     |   Added subTechniques in Template                                  |
| 3.0.0       | 12-12-2023                     |   Fixed **Playbooks** issue                                        |

[← Back to Solutions Index](../solutions-index.md)
