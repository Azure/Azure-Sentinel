# ExtraHop Reveal(x)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ExtraHop |
| **Support Tier** | Partner |
| **Support Link** | [https://www.extrahop.com/support/](https://www.extrahop.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] ExtraHop Reveal(x) via Legacy Agent](../connectors/extrahopnetworks.md)

**Publisher:** ExtraHop Networks

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ExtraHopNetworks.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopNetworks.json) |

[→ View full connector details](../connectors/extrahopnetworks.md)

### [[Deprecated] ExtraHop Reveal(x) via AMA](../connectors/extrahopnetworksama.md)

**Publisher:** ExtraHop Networks

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ExtraHopReveal%28x%29AMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopReveal%28x%29AMA.json) |

[→ View full connector details](../connectors/extrahopnetworksama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] ExtraHop Reveal(x) via AMA](../connectors/extrahopnetworksama.md), [[Deprecated] ExtraHop Reveal(x) via Legacy Agent](../connectors/extrahopnetworks.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 11-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 13-09-2023                     |	Addition of new ExtraHop Reveal(x) AMA **Data Connector**       |

[← Back to Solutions Index](../solutions-index.md)
