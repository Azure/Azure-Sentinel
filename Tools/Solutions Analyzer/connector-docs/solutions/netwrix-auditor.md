# Netwrix Auditor

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Netwrix Auditor via Legacy Agent

**Publisher:** Netwrix

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Connector_NetwrixAuditor.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Data%20Connectors/Connector_NetwrixAuditor.json)

### [Deprecated] Netwrix Auditor via AMA

**Publisher:** Netwrix

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_NetwrixAuditorAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Data%20Connectors/template_NetwrixAuditorAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n