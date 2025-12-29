# Akamai Security Events

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Akamai Security Events via Legacy Agent](../connectors/akamaisecurityevents.md)

**Publisher:** Akamai

Akamai Solution for Microsoft Sentinel provides the capability to ingest [Akamai Security Events](https://www.akamai.com/us/en/products/security/) into Microsoft Sentinel. Refer to [Akamai SIEM Integration documentation](https://developer.akamai.com/tools/integrations/siem) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_CEF_Akamai.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events/Data%20Connectors/Connector_CEF_Akamai.json) |

[→ View full connector details](../connectors/akamaisecurityevents.md)

### [[Deprecated] Akamai Security Events via AMA](../connectors/akamaisecurityeventsama.md)

**Publisher:** Akamai

Akamai Solution for Microsoft Sentinel provides the capability to ingest [Akamai Security Events](https://www.akamai.com/us/en/products/security/) into Microsoft Sentinel. Refer to [Akamai SIEM Integration documentation](https://developer.akamai.com/tools/integrations/siem) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_AkamaiSecurityEventsAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events/Data%20Connectors/template_AkamaiSecurityEventsAMA.json) |

[→ View full connector details](../connectors/akamaisecurityeventsama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Akamai Security Events via AMA](../connectors/akamaisecurityeventsama.md), [[Deprecated] Akamai Security Events via Legacy Agent](../connectors/akamaisecurityevents.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 12-11-2024                     |    Removed Deprecated **Data Connector**                           |
| 3.0.1       | 08-07-2024                     |    Deprecated **Data Connector**                                   |
| 3.0.0       | 20-09-2023                     |    Addition of new Akamai Security Events AMA **Data Connector**   |

[← Back to Solutions Index](../solutions-index.md)
