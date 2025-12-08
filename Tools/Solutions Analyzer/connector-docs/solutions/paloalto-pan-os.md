# PaloAlto-PAN-OS

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md)

**Publisher:** Palo Alto Networks

The Palo Alto Networks firewall connector allows you to easily connect your Palo Alto Networks logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PaloAltoNetworksAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Data%20Connectors/template_PaloAltoNetworksAMA.json) |

[→ View full connector details](../connectors/paloaltonetworksama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md), [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md) |

[← Back to Solutions Index](../solutions-index.md)
