# NXLogDnsLogs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | NXLog |
| **Support Tier** | Partner |
| **Support Link** | [https://nxlog.co/support-tickets/add/support-ticket](https://nxlog.co/support-tickets/add/support-ticket) |
| **Categories** | domains |
| **First Published** | 2022-05-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [NXLog DNS Logs](../connectors/nxlogdnslogs.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md) | [NXLog DNS Logs](../connectors/nxlogdnslogs.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ASimDnsMicrosoftNXLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs/Parsers/ASimDnsMicrosoftNXLog.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
