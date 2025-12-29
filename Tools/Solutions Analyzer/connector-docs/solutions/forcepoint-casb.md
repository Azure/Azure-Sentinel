# Forcepoint CASB

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Forcepoint CASB via Legacy Agent](../connectors/forcepointcasb.md)

**Publisher:** Forcepoint CASB

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Forcepoint%20CASB.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/Forcepoint%20CASB.json) |

[→ View full connector details](../connectors/forcepointcasb.md)

### [[Deprecated] Forcepoint CASB via AMA](../connectors/forcepointcasbama.md)

**Publisher:** Forcepoint CASB

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_Forcepoint%20CASBAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/template_Forcepoint%20CASBAMA.json) |

[→ View full connector details](../connectors/forcepointcasbama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint CASB via AMA](../connectors/forcepointcasbama.md), [[Deprecated] Forcepoint CASB via Legacy Agent](../connectors/forcepointcasb.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 27-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.1       | 15-07-2024                     |	Deprecating data connectors                                     |
| 3.0.0       | 31-08-2023                     |	Addition of new Forcepoint CASB AMA **Data Connector**          |

[← Back to Solutions Index](../solutions-index.md)
