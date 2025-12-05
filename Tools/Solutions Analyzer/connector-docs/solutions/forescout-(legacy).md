# Forescout (Legacy)

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20%28Legacy%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20%28Legacy%29) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forescout](../connectors/forescout.md)

**Publisher:** Forescout

The [Forescout](https://www.forescout.com/) data connector provides the capability to ingest [Forescout events](https://docs.forescout.com/bundle/syslog-3-6-1-h/page/syslog-3-6-1-h.How-to-Work-with-the-Syslog-Plugin.html) into Microsoft Sentinel. Refer to [Forescout documentation](https://docs.forescout.com/bundle/syslog-msg-3-6-tn/page/syslog-msg-3-6-tn.About-Syslog-Messages-in-Forescout.html) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Forescout_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forescout%20%28Legacy%29/Data%20Connectors/Forescout_syslog.json) |

[→ View full connector details](../connectors/forescout.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [Forescout](../connectors/forescout.md) |

[← Back to Solutions Index](../solutions-index.md)
