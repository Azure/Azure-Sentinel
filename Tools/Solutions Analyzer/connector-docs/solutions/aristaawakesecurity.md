# AristaAwakeSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Arista - Awake Security |
| **Support Tier** | Partner |
| **Support Link** | [https://awakesecurity.com/](https://awakesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Awake Security via Legacy Agent](../connectors/aristaawakesecurity.md)

**Publisher:** Arista Networks

The Awake Security CEF connector allows users to send detection model matches from the Awake Security Platform to Microsoft Sentinel. Remediate threats quickly with the power of network detection and response and speed up investigations with deep visibility especially into unmanaged entities including users, devices and applications on your network. The connector also enables the creation of network security-focused custom alerts, incidents, workbooks and notebooks that align with your existing security operations workflows. 

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_AristaAwakeSecurity_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Data%20Connectors/Connector_AristaAwakeSecurity_CEF.json) |

[→ View full connector details](../connectors/aristaawakesecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Awake Security via Legacy Agent](../connectors/aristaawakesecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
