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

The Windows DNS log connector allows you to easily filter and stream all analytics logs from your Windows DNS servers to your Microsoft Sentinel workspace using the Azure Monitoring agent (AMA). Having this data in Microsoft Sentinel helps you identify issues and security threats such as:

- Trying to resolve malicious domain names.

- Stale resource records.

- Frequently queried domain names and talkative DNS clients.

- Attacks performed on DNS server.



You can get the following insights into your Windows DNS servers from Microsoft Sentinel:

- All logs centralized in a single place.

- Request load on DNS servers.

- Dynamic DNS registration failures.



Windows DNS events are supported by Advanced SIEM Information Model (ASIM) and stream data into the ASimDnsActivityLogs table. [Learn more](https://docs.microsoft.com/azure/sentinel/normalization).



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2225993&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `ASimDnsActivityLogs` |
| **Connector Definition Files** | [template_ASimDnsActivityLogs.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Data%20Connectors/template_ASimDnsActivityLogs.JSON) |

[→ View full connector details](../connectors/asimdnsactivitylogs.md)

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
| `ASimDnsActivityLogs` | Windows DNS Events via AMA |
| `DnsEvents` | DNS |
| `DnsInventory` | DNS |

[← Back to Solutions Index](../solutions-index.md)
