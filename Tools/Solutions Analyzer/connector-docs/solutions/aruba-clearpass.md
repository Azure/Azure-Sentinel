# Aruba ClearPass

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Aruba ClearPass via Legacy Agent](../connectors/arubaclearpass.md)

**Publisher:** Aruba Networks

### [[Deprecated] Aruba ClearPass via AMA](../connectors/arubaclearpassama.md)

**Publisher:** Aruba Networks

The [Aruba ClearPass](https://www.arubanetworks.com/products/security/network-access-control/secure-access/) connector allows you to easily connect your Aruba ClearPass with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ArubaClearPassAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass/Data%20Connectors/template_ArubaClearPassAMA.json) |

[→ View full connector details](../connectors/arubaclearpassama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Aruba ClearPass via AMA](../connectors/arubaclearpassama.md), [[Deprecated] Aruba ClearPass via Legacy Agent](../connectors/arubaclearpass.md) |

[← Back to Solutions Index](../solutions-index.md)
