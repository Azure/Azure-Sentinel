# archTIS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | archTIS |
| **Support Tier** | Partner |
| **Support Link** | [https://www.archtis.com/nc-protect-support/](https://www.archtis.com/nc-protect-support/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [NC Protect](../connectors/nucleuscyberncprotect.md)

**Publisher:** archTIS

[NC Protect Data Connector (archtis.com)](https://info.archtis.com/get-started-with-nc-protect-sentinel-data-connector) provides the capability to ingest user activity logs and events into Microsoft Sentinel. The connector provides visibility into NC Protect user activity logs and events in Microsoft Sentinel to improve monitoring and investigation capabilities

| | |
|--------------------------|---|
| **Tables Ingested** | `NCProtectUAL_CL` |
| **Connector Definition Files** | [NucleusCyberNCProtect.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS/Data%20Connectors/NucleusCyberNCProtect.json) |

[→ View full connector details](../connectors/nucleuscyberncprotect.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NCProtectUAL_CL` | [NC Protect](../connectors/nucleuscyberncprotect.md) |

[← Back to Solutions Index](../solutions-index.md)
