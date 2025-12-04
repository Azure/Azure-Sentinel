# McAfee ePolicy Orchestrator

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-03-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] McAfee ePolicy Orchestrator (ePO)](../connectors/mcafeeepo.md)

**Publisher:** McAfee

The McAfee ePolicy Orchestrator data connector provides the capability to ingest [McAfee ePO](https://www.mcafee.com/enterprise/en-us/products/epolicy-orchestrator.html) events into Microsoft Sentinel through the syslog. Refer to [documentation](https://docs.mcafee.com/bundle/epolicy-orchestrator-landing/page/GUID-0C40020F-5B7F-4549-B9CC-0E017BC8797F.html) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_McAfee_ePO.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Data%20Connectors/Connector_McAfee_ePO.json) |

[→ View full connector details](../connectors/mcafeeepo.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] McAfee ePolicy Orchestrator (ePO)](../connectors/mcafeeepo.md) |

[← Back to Solutions Index](../solutions-index.md)
