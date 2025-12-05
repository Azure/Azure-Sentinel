# Valence Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Valence Security |
| **Support Tier** | Partner |
| **Support Link** | [https://www.valencesecurity.com/](https://www.valencesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2023-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SaaS Security](../connectors/valencesecurity.md)

**Publisher:** Valence Security

Connects the Valence SaaS security platform Azure Log Analytics via the REST API interface.

| | |
|--------------------------|---|
| **Tables Ingested** | `ValenceAlert_CL` |
| **Connector Definition Files** | [ValenceSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security/Data%20Connectors/ValenceSecurity.json) |

[→ View full connector details](../connectors/valencesecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ValenceAlert_CL` | [SaaS Security](../connectors/valencesecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
