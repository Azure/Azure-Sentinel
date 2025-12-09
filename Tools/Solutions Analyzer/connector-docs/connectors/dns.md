# DNS

| | |
|----------|-------|
| **Connector ID** | `DNS` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`DnsEvents`](../tables-index.md#dnsevents), [`DnsInventory`](../tables-index.md#dnsinventory) |
| **Used in Solutions** | [Windows Server DNS](../solutions/windows-server-dns.md) |
| **Connector Definition Files** | [template_DNS.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Data%20Connectors/template_DNS.JSON) |

The DNS log connector allows you to easily connect your DNS analytic and audit logs with Microsoft Sentinel, and other related data, to improve investigation.



**When you enable DNS log collection you can:**

-   Identify clients that try to resolve malicious domain names.

-   Identify stale resource records.

-   Identify frequently queried domain names and talkative DNS clients.

-   View request load on DNS servers.

-   View dynamic DNS registration failures.



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220127&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
