# Windows Server DNS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Windows DNS Events via AMA](../connectors/asimdnsactivitylogs.md)

**Publisher:** Microsoft

### [DNS](../connectors/dns.md)

**Publisher:** Microsoft

The DNS log connector allows you to easily connect your DNS analytic and audit logs with Microsoft Sentinel, and other related data, to improve investigation.



**When you enable DNS log collection you can:**

-   Identify clients that try to resolve malicious domain names.

-   Identify stale resource records.

-   Identify frequently queried domain names and talkative DNS clients.

-   View request load on DNS servers.

-   View dynamic DNS registration failures.



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220127&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `DnsEvents` |
| | `DnsInventory` |
| **Connector Definition Files** | [template_DNS.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Data%20Connectors/template_DNS.JSON) |

[→ View full connector details](../connectors/dns.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimDnsActivityLogs` | [Windows DNS Events via AMA](../connectors/asimdnsactivitylogs.md) |
| `DnsEvents` | [DNS](../connectors/dns.md) |
| `DnsInventory` | [DNS](../connectors/dns.md) |

[← Back to Solutions Index](../solutions-index.md)
