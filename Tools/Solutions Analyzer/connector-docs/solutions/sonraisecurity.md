# SonraiSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Sonrai |
| **Support Tier** | Partner |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Sonrai Data Connector](../connectors/sonraidataconnector.md)

**Publisher:** Sonrai

Use this data connector to integrate with Sonrai Security and get Sonrai tickets sent directly to Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Sonrai_Tickets_CL` |
| **Connector Definition Files** | [Connector_REST_API_Sonrai.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Data%20Connectors/Connector_REST_API_Sonrai.json) |

[→ View full connector details](../connectors/sonraidataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Sonrai_Tickets_CL` | [Sonrai Data Connector](../connectors/sonraidataconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 04-12-2023                     | Added entity mapping to **Analytic Rules**                               |

[← Back to Solutions Index](../solutions-index.md)
