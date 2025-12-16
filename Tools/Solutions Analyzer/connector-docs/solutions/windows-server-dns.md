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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Solutions** (ResourceGroup): [read and write permissions](https://docs.microsoft.com/azure/role-based-access-control/built-in-roles#log-analytics-contributor).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Download and install the agent**

>  DNS logs are collected only from **Windows** agents.
**Choose where to install the agent:**

**Install agent on Azure Windows Virtual Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on non-Azure Windows Machine**

  Select the machine to install the agent and then click **Connect**.
  - **Install/configure: InstallAgentOnNonAzure**

**2. Install DNS solution**
- Install solution: DnsAnalytics

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
