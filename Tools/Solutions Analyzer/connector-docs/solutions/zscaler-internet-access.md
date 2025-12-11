# Zscaler Internet Access

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Zscaler |
| **Support Tier** | Partner |
| **Support Link** | [https://help.zscaler.com/submit-ticket-links](https://help.zscaler.com/submit-ticket-links) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Zscaler via Legacy Agent](../connectors/zscaler.md)

**Publisher:** Zscaler

### [[Deprecated] Zscaler via AMA](../connectors/zscalerama.md)

**Publisher:** Zscaler

The Zscaler data connector allows you to easily connect your Zscaler Internet Access (ZIA) logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.  Using Zscaler on Microsoft Sentinel will provide you more insights into your organization’s Internet usage, and will enhance its security operation capabilities.​

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ZscalerAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Data%20Connectors/template_ZscalerAma.JSON) |

[→ View full connector details](../connectors/zscalerama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Zscaler via AMA](../connectors/zscalerama.md), [[Deprecated] Zscaler via Legacy Agent](../connectors/zscaler.md) |

[← Back to Solutions Index](../solutions-index.md)
