# Vectra AI Detect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Vectra AI |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2022-05-24 |
| **Last Updated** | 2023-04-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Vectra AI Detect via Legacy Agent](../connectors/aivectradetect.md)

**Publisher:** Vectra AI

### [[Deprecated] Vectra AI Detect via AMA](../connectors/aivectradetectama.md)

**Publisher:** Vectra AI

The AI Vectra Detect connector allows users to connect Vectra Detect logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives users more insight into their organization's network and improves their security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_AIVectraDetectAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Data%20Connectors/template_AIVectraDetectAma.json) |

[→ View full connector details](../connectors/aivectradetectama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Vectra AI Detect via AMA](../connectors/aivectradetectama.md), [[Deprecated] Vectra AI Detect via Legacy Agent](../connectors/aivectradetect.md) |

[← Back to Solutions Index](../solutions-index.md)
