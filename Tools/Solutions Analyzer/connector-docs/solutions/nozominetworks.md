# NozomiNetworks

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Nozomi Networks N2OS via Legacy Agent

**Publisher:** Nozomi Networks

The [Nozomi Networks](https://www.nozominetworks.com/) data connector provides the capability to ingest Nozomi Networks Events into Microsoft Sentinel. Refer to the Nozomi Networks [PDF documentation](https://www.nozominetworks.com/resources/data-sheets-brochures-learning-guides/) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [NozomiNetworksN2OS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks/Data%20Connectors/NozomiNetworksN2OS.json)

### [Deprecated] Nozomi Networks N2OS via AMA

**Publisher:** Nozomi Networks

The [Nozomi Networks](https://www.nozominetworks.com/) data connector provides the capability to ingest Nozomi Networks Events into Microsoft Sentinel. Refer to the Nozomi Networks [PDF documentation](https://www.nozominetworks.com/resources/data-sheets-brochures-learning-guides/) for more information.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_NozomiNetworksN2OSAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks/Data%20Connectors/template_NozomiNetworksN2OSAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n