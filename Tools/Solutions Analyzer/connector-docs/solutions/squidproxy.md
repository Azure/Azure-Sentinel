# SquidProxy

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Squid Proxy](../connectors/squidproxy.md)

**Publisher:** Squid

The [Squid Proxy](http://www.squid-cache.org/) connector allows you to easily connect your Squid Proxy logs with Microsoft Sentinel. This gives you more insight into your organization's network proxy traffic and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `SquidProxy_CL` |
| **Connector Definition Files** | [Connector_CustomLog_SquidProxy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SquidProxy/Data%20Connectors/Connector_CustomLog_SquidProxy.json) |

[→ View full connector details](../connectors/squidproxy.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SquidProxy_CL` | [[Deprecated] Squid Proxy](../connectors/squidproxy.md) |

[← Back to Solutions Index](../solutions-index.md)
