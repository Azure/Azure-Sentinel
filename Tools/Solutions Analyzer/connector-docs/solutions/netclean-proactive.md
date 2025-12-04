# NetClean ProActive

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | NetClean |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netclean.com/contact](https://www.netclean.com/contact) |
| **Categories** | domains |
| **First Published** | 2022-06-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Netclean ProActive Incidents](../connectors/netclean-proactive-incidents.md)

**Publisher:** NetClean Technologies

This connector uses the Netclean Webhook (required) and Logic Apps to push data into Microsoft Sentinel Log Analytics

| | |
|--------------------------|---|
| **Tables Ingested** | `Netclean_Incidents_CL` |
| **Connector Definition Files** | [Connector_NetClean.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive/Data%20Connectors/Connector_NetClean.json) |

[→ View full connector details](../connectors/netclean-proactive-incidents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Netclean_Incidents_CL` | [Netclean ProActive Incidents](../connectors/netclean-proactive-incidents.md) |

[← Back to Solutions Index](../solutions-index.md)
