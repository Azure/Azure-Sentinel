# Egress Defend

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | egress1589289169584 |
| **Support Tier** | Partner |
| **Support Link** | [https://support.egress.com/s/](https://support.egress.com/s/) |
| **Categories** | domains |
| **First Published** | 2023-07-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Egress Defend](../connectors/egressdefendpolling.md)

**Publisher:** Egress Software Technologies

The Egress Defend audit connector provides the capability to ingest Egress Defend Data into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions on the Log Analytics workspace are required to enable the data connector.

**Custom Permissions:**
- **Egress API Token**: An Egress API token is required to ingest audit records to Microsoft Sentinel.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Egress Defend with Microsoft Sentinel**

Enter your Egress Defend API URl, Egress Domain and API token.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `EgressDefend_CL` |
| **Connector Definition Files** | [DefendAPIConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Data%20Connectors/DefendAPIConnector.json) |

[→ View full connector details](../connectors/egressdefendpolling.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `EgressDefend_CL` | [Egress Defend](../connectors/egressdefendpolling.md) |

[← Back to Solutions Index](../solutions-index.md)
