# Syslog

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Syslog via Legacy Agent](../connectors/syslog.md)
- [Syslog via AMA](../connectors/syslogama.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`FinalSummary`](../tables/finalsummary.md) | - | Hunting |
| [`Syslog`](../tables/syslog.md) | [Syslog via AMA](../connectors/syslogama.md), [Syslog via Legacy Agent](../connectors/syslog.md) | Analytics, Hunting, Workbooks |
| [`scx_execve`](../tables/scx-execve.md) | - | Hunting |

## Content Items

This solution includes **18 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 9 |
| Analytic Rules | 7 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Failed logon attempts in authpriv](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/FailedLogonAttempts_UnknownUser.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [NRT Squid proxy events related to mining pools](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/NRT_squid_events_for_mining_pools.yaml) | Low | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [SFTP File transfer above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/sftp_file_transfer_above_threshold.yaml) | Medium | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [SFTP File transfer folder count above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/sftp_file_transfer_folders_above_threshold.yaml) | Medium | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [SSH - Potential Brute Force](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/ssh_potentialBruteForce.yaml) | Low | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [Squid proxy events for ToR proxies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/squid_tor_proxies.yaml) | Low | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Squid proxy events related to mining pools](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/squid_cryptomining_pools.yaml) | Low | CommandAndControl | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Crypto currency miners EXECVE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/CryptoCurrencyMiners.yaml) | Persistence, Execution | [`Syslog`](../tables/syslog.md) |
| [Editing Linux scheduled tasks through Crontab](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/SchedTaskEditViaCrontab.yaml) | Persistence, Execution | [`Syslog`](../tables/syslog.md) |
| [Linux scheduled task Aggregation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/SchedTaskAggregation.yaml) | Persistence, Execution | [`FinalSummary`](../tables/finalsummary.md)<br>[`Syslog`](../tables/syslog.md) |
| [Rare process running on a Linux host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/RareProcess_ForLxHost.yaml) | Execution, Persistence | [`Syslog`](../tables/syslog.md) |
| [SCX Execute RunAs Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/SCXExecuteRunAsProviders.yaml) | InitialAccess, Execution | [`Syslog`](../tables/syslog.md)<br>[`scx_execve`](../tables/scx-execve.md) |
| [Squid commonly abused TLDs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/squid_abused_tlds.yaml) | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Squid data volume timeseries anomalies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/squid_volume_anomalies.yaml) | CommandAndControl, Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Squid malformed requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/squid_malformed_requests.yaml) | Discovery | [`Syslog`](../tables/syslog.md) |
| [Suspicious crytocurrency mining related threat activity detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/CryptoThreatActivity.yaml) | DefenseEvasion | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [LinuxMachines](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Workbooks/LinuxMachines.json) | [`Syslog`](../tables/syslog.md) |
| [SyslogConnectorsOverviewWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Workbooks/SyslogConnectorsOverviewWorkbook.json) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.7       | 04-11-2024                     |  Updated the Syslog **Data Connector** template to latest version  |
| 3.0.6       | 01-08-2024                     |  Updated **Analytic rules** for entity mappings and parameter for parser function  |
| 3.0.5       | 16-07-2024                     |  Added 2 new Workspace Function **Parsers** and a new **Workbook**       |
| 3.0.4       | 27-06-2024                     |  Updated Connectivity criteria query for **Data Connector**        |
| 3.0.3       | 10-04-2024                     |  Updated Entity Mappings **Analytic Rule** FailedLogonAttempts_UnknownUser.yaml    |
| 3.0.2       | 21-02-2024                     |  Addition of new Syslog AMA **Data Connector**                     |
| 3.0.1       | 01-02-2024                     |  **Hunting Queries** Description updated                           |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
