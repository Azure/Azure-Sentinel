# Windows DNS Events via AMA

| | |
|----------|-------|
| **Connector ID** | `ASimDnsActivityLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ASimDnsActivityLogs`](../tables-index.md#asimdnsactivitylogs) |
| **Used in Solutions** | [Windows Server DNS](../solutions/windows-server-dns.md) |
| **Connector Definition Files** | [template_ASimDnsActivityLogs.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Data%20Connectors/template_ASimDnsActivityLogs.JSON) |

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

## Permissions

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `ASimDnsActivityLogs`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
