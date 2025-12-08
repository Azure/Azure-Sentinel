# ExtraHop Reveal(x)

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] ExtraHop Reveal(x) via AMA](../connectors/extrahopnetworksama.md)

**Publisher:** ExtraHop Networks

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ExtraHopReveal%28x%29AMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopReveal%28x%29AMA.json) |

[→ View full connector details](../connectors/extrahopnetworksama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] ExtraHop Reveal(x) via AMA](../connectors/extrahopnetworksama.md), [[Deprecated] ExtraHop Reveal(x) via Legacy Agent](../connectors/extrahopnetworks.md) |

[← Back to Solutions Index](../solutions-index.md)
