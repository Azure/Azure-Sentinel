# Forcepoint CASB

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Forcepoint CASB via Legacy Agent

**Publisher:** Forcepoint CASB

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Forcepoint%20CASB.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/Forcepoint%20CASB.json)

### [Deprecated] Forcepoint CASB via AMA

**Publisher:** Forcepoint CASB

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_Forcepoint%20CASBAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/template_Forcepoint%20CASBAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n