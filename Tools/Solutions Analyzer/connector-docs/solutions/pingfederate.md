# PingFederate

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] PingFederate via Legacy Agent

**Publisher:** Ping Identity

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Connector_CEF_PingFederate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Data%20Connectors/Connector_CEF_PingFederate.json)

### [Deprecated] PingFederate via AMA

**Publisher:** Ping Identity

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_PingFederateAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Data%20Connectors/template_PingFederateAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n