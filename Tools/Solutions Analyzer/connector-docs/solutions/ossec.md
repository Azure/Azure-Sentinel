# OSSEC

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] OSSEC via Legacy Agent

**Publisher:** OSSEC

OSSEC data connector provides the capability to ingest [OSSEC](https://www.ossec.net/) events into Microsoft Sentinel. Refer to [OSSEC documentation](https://www.ossec.net/docs) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Connector_CEF_OSSEC.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC/Data%20Connectors/Connector_CEF_OSSEC.json)

### [Deprecated] OSSEC via AMA

**Publisher:** OSSEC

OSSEC data connector provides the capability to ingest [OSSEC](https://www.ossec.net/) events into Microsoft Sentinel. Refer to [OSSEC documentation](https://www.ossec.net/docs) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_OSSECAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC/Data%20Connectors/template_OSSECAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n