# Forcepoint CASB

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Forcepoint CASB via AMA](../connectors/forcepointcasbama.md)

**Publisher:** Forcepoint CASB

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_Forcepoint%20CASBAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/template_Forcepoint%20CASBAMA.json) |

[→ View full connector details](../connectors/forcepointcasbama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint CASB via AMA](../connectors/forcepointcasbama.md), [[Deprecated] Forcepoint CASB via Legacy Agent](../connectors/forcepointcasb.md) |

[← Back to Solutions Index](../solutions-index.md)
